from django.shortcuts import render
import requests
from django.http import HttpResponse
from models import *
from tasks import update_user

def escape(name):
    return name.replace("\"", "\\\\\\\"")

def digraph(tree):
    if tree.game_node:
        result = "\t%s [label=\\\"%s\\\", shape=box]\\\n" % (tree.name, ",\\n".join(sorted([escape(x.name) for x in tree.games.all()])))
    else:
        result = "\t%s [label=\\\"%s\\\"]\\\n" % (tree.name, tree.description)
        for to_node in tree.questions.all():
            res = digraph(to_node)
            result += "\t%s -> %s [label=\\\"%s\\\"]\\\n" %(tree.name, to_node.name, QuestionLink.objects.get(from_node=tree, to_node=to_node).label)
            result += res
    return result

def user(request, name):
    users = User.objects.filter(name=name)
    if not users.exists() or users.first().root_node == None:
        update_user.delay(name)
        raise Exception
    else:
        user = users.first()
        output = digraph(user.root_node)
        return render(request, "graph.html", {
            "output": output,
            "user": name
            })
