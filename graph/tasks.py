from .celery import app
from .models import User, Game, TreeNode, QuestionLink
import xml.etree.ElementTree as ET
import itertools
from typing import List
import requests
import logging

logger = logging.getLogger(__name__)

def fill_tree(question_index, games):
    games = set([x["id"] for x in list(games.values())])
    for question in list(question_index.values()):
        if "default" in question:
            non_default = set(itertools.chain.from_iterable([question["options"][k] for k in list(question["options"].keys()) if k != question["default"]]))
            question["options"][question["default"]] = list(games-non_default)

def question_value(question, total):
    values = dict([(k, len(question["options"][k])) for k in list(question["options"].keys())])
    local_total = sum(values.values())
    if local_total < total:
        raise Exception(local_total, total, question)
    return min(values.values())

def best_question(question_index, games):
    total = len(games)
    ordered = sorted(list(question_index.items()), key=lambda x: question_value(x[1], total), reverse=True)
    if len(ordered) == 0:
        return None
    return ordered[0][0]

def remove_games(question_index, removed_games, most_asked):
    new_question_index = {}
    for k in list(question_index.keys()):
        if k == most_asked:
            continue
        new_question_index[k] = {"options": {}}
        for o in list(question_index[k]["options"].keys()):
            items = set(question_index[k]["options"][o])-removed_games
            if len(items) > 0:
                new_question_index[k]["options"][o] = items
        if len([x for x in list(new_question_index[k]["options"].values()) if len(x)>0]) < 2 or sum([len(x) for x in list(new_question_index[k]["options"].values())]) == 0:
            del new_question_index[k]
    return new_question_index

def build_tree(question_index, items):
    games = set(x["id"] for x in list(items.values()))
    most_asked = best_question(question_index, items)
    if most_asked == None:
        return list(items.keys())
    question = question_index[most_asked]
    tree = {"question": most_asked, "options": {}}
    for k in list(question["options"].keys()):
        removed_games = games-set(question["options"][k])
        nq = remove_games(question_index, removed_games, most_asked)
        tree["options"][k] = build_tree(nq, {k: v for k, v in items.items() if v["id"] not in removed_games})
    return tree

def flatten_name(name):
    if name == '':
        return ''
    if name[0].isdigit():
        name = "_" + name
    return name \
        .replace(" ", "_") \
        .replace("?", "") \
        .replace(":", "") \
        .replace("/", "") \
        .replace("-", "_") \
        .replace("&", "and") \
        .replace("'", "") \
        .replace("!", "") \
        .replace(",", "") \
        .replace(".","") \
        .lower()

def digraph(tree):
    if type(tree) == List:
        flat_question = flatten_name(" ".join([str(x) for x in tree]))
    else:
        flat_question = flatten_name(tree["question"])
    flat_question = ("%s_%d" %(flat_question, id(tree)))[:200]
    if type(tree) == List:
        node, _ = TreeNode.objects.get_or_create(name=flat_question, game_node=True)
        for x in tree:
            node.games.add(Game.objects.get(id=x))
        node.save()
    else:
        node, _ = TreeNode.objects.get_or_create(name=flat_question, description=tree["question"], game_node=False)
        for k in tree["options"]:
            subnode = digraph(tree["options"][k])
            QuestionLink.objects.get_or_create(from_node=node, to_node=subnode, label=k)
    return node

@app.task(bind=True)
def update_user(self, name):
    users = User.objects.filter(name=name)
    if not users.exists():
        user = User.objects.create(name=name)
    else:
        user = users.first()
    if user.xml == "":
        logger.info("Get user %s", name)
        url = "https://www.boardgamegeek.com/xmlapi2/collection?username=%s&subtype=boardgame&excludessubtype=boardgameexpansion" % name
        info = requests.get(url)
        info.raise_for_status()
        user.xml=info.text
        user.save()
        xml = info.text
    else:
        xml = user.xml
    root = ET.fromstring(xml.encode('utf-8'))
    items = {}
    question_index = {}
    if root.tag in ["errors", "message"]:
        user.processing_task = None
        user.save()
        return
    for item in root.findall("item"):
        validitem = True
        for child in item:
            if child.tag == "status":
                if child.get("own") != "1":
                    validitem = False
                    break
        if not validitem:
            continue
        game = int(item.get("objectid"))
        games = Game.objects.filter(id=game)
        if not games.exists():
            logger.info("Get game %s", game)
            url = "https://www.boardgamegeek.com/xmlapi2/thing?id=%d" % game
            info = requests.get(url)
            gameroot = ET.fromstring(info.text.encode('utf-8'))[0]
            name = game
            for nametag in gameroot.findall("name"):
                if nametag.get("type") == "primary":
                    name = nametag.get("value")
                    break
            Game.objects.get_or_create(id=game, defaults={"xml": info.text, "name": name})
        else:
            gameroot = ET.fromstring(games[0].xml.encode('utf-8'))[0]
        questions = []
        for linktag in gameroot.findall("link"):
            if linktag.get("type") == "boardgamemechanic":
                text = "%s?" % linktag.get("value")
                if text not in question_index:
                    question_index[text] = {"options":{"Yes":[], "No":[]}, "default": "No"}
                question_index[text]["options"]["Yes"].append(game)
                questions.append({"text": text, "answer":"Yes"})
        items[game] = {"id": game, "answers": questions}
    fill_tree(question_index, items)
    tree = build_tree(question_index, items)
    output = digraph(tree)
    user.root_node = output
    user.processing_task = None
    user.save()