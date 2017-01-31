from django.shortcuts import render
import requests
from django.http import HttpResponse
from models import *
import xml.etree.ElementTree as ET
import pprint
import itertools

def fill_tree(question_index, games):
    games = set([x["id"] for x in games.values()])
    for question in question_index.values():
        if "default" in question:
            non_default = set(itertools.chain.from_iterable([question["options"][k] for k in question["options"].keys() if k != question["default"]]))
            question["options"][question["default"]] = list(games-non_default)

def question_value(question, total):
    values = dict([(k, len(question["options"][k])) for k in question["options"].keys()])
    local_total = sum(values.values())
    if local_total < total:
        raise Exception, (local_total, total, question)
    return min(values.values())

def best_question(question_index, games):
    total = len(games)
    ordered = sorted(question_index.items(), key=lambda x: question_value(x[1], total), reverse=True)
    if len(ordered) == 0:
        return None
    return ordered[0][0]

def remove_games(question_index, removed_games, most_asked):
    new_question_index = {}
    for k in question_index.keys():
        if k == most_asked:
            continue
        new_question_index[k] = {"options": {}}
        for o in question_index[k]["options"].keys():
            items = set(question_index[k]["options"][o])-removed_games
            if len(items) > 0:
                new_question_index[k]["options"][o] = items
        if len([x for x in new_question_index[k]["options"].values() if len(x)>0]) < 2 or sum([len(x) for x in new_question_index[k]["options"].values()]) == 0:
            del new_question_index[k]
    return new_question_index

def build_tree(question_index, items):
    games = set(x["id"] for x in items.values())
    most_asked = best_question(question_index, items)
    if most_asked == None:
        return items.keys()
    question = question_index[most_asked]
    tree = {"question": most_asked, "options": {}}
    for k in question["options"].keys():
        removed_games = games-set(question["options"][k])
        nq = remove_games(question_index, removed_games, most_asked)
        tree["options"][k] = build_tree(nq, {k: v for k, v in items.iteritems() if v["id"] not in removed_games})
    return tree

def user(request, name):
    users = User.objects.filter(name=name)
    if not users.exists():
        url = "https://www.boardgamegeek.com/xmlapi2/collection?username=%s&subtype=boardgame&excludessubtype=boardgameexpansion" % name
        info = requests.get(url)
        User.objects.create(name=name, xml=info.text)
        xml = info.text
    else:
        xml = users[0].xml
    root = ET.fromstring(xml)
    items = {}
    question_index = {}
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
            url = "https://www.boardgamegeek.com/xmlapi2/thing?id=%d" % game
            info = requests.get(url)
            Game.objects.create(id=game, xml=info.text)
            xml = info.text
        else:
            xml = games[0].xml
        gameroot = ET.fromstring(xml.encode('utf-8'))[0]
        name = game
        for nametag in gameroot.findall("name"):
            if nametag.get("type") == "primary":
                name = nametag.get("value")
                break
        questions = []
        for linktag in gameroot.findall("link"):
            if linktag.get("type") == "boardgamemechanic":
                text = "%s?" % linktag.get("value")
                if text not in question_index:
                    question_index[text] = {"options":{"Yes":[], "No":[]}, "default": "No"}
                question_index[text]["options"]["Yes"].append(game)
                questions.append({"text": text, "answer":"Yes"})
        items[name] = {"id": game, "answers": questions}
    fill_tree(question_index, items)
    tree = build_tree(question_index, items)
    raise Exception, tree
    most_asked = best_question(question_index, items)
    return HttpResponse("<pre>" + pprint.pformat(question_index) + "<br />" + pprint.pformat(items))

