from django.shortcuts import render, redirect
import requests
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from models import *
from tasks import update_user
from celery import app
import xml.etree.ElementTree as ET
import urllib

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

def index(request):
    return render(request, "index.html")

def user(request, name):
    users = User.objects.filter(name=name)
    if not users.exists():
        user = User.objects.create(name=name)
        task = update_user.delay(name)
        user.processing_task=task.id
        user.save()
        return redirect("/pending/%s" % name)
    user = users.first()
    if user.root_node == None:
        if user.processing_task is not None:
            return redirect("/pending/%s" % name)
        task = update_user.delay(name)
        user.processing_task = task.id
        user.save()
        return redirect("/pending/%s" % name)
    question = user.root_node
    existing = {}
    while True:
        if question.description in request.GET:
            existing[question.description] = request.GET[question.description]
            question = QuestionLink.objects.filter(from_node=question, label=existing[question.description]).first().to_node
        else:
            break
    if question.game_node:
        all_games = list(question.games.all())
        if len(all_games) == 0:
            return render(request, "nogames.html", {
                "user": name
            })
        last_game = all_games[-1]
        return render(request, "games.html", {
            "user": name,
            "rest": all_games[:-1],
            "last": all_games[-1],
            "existing": existing
        })
    answers = {}
    questions = QuestionLink.objects.filter(from_node=question)
    for answer in questions.all():
        answers[answer.label] = existing.copy()
        answers[answer.label][question.description] = answer.label
        answers[answer.label] = "&".join(["%s=%s"%(urllib.quote(key),value) for (key,value) in answers[answer.label].items()])
    return render(request, "question.html", {
        "existing": existing,
        "question": question.description,
        "user": name,
        "answers": answers
        })

def graph(request, name):
    users = User.objects.filter(name=name)
    if not users.exists():
        return redirect("/user/%s" % name)
    user = users.first()
    if user.root_node == None:
        return redirect("/user/%s" % name)
    output = digraph(user.root_node)
    return render(request, "graph.html", {
        "output": output,
        "user": name
        })

def user_refresh(request, name):
    users = User.objects.filter(name=name)
    if not users.exists():
        return HttpResponseNotFound()
    user = users.first()
    user.xml = ""
    task = update_user.delay(name)
    user.processing_task = task.id
    user.save()
    return JsonResponse({"message:":"refreshing..."})

def lookup(request):
    return redirect("/user/%s" % request.POST["username"])

def pending(request, name):
    return render(request, "pending.html", {
        "user": name
        })

def status(request, name):
    user = User.objects.get(name=name)
    if user.processing_task != None: # might have items, but should tell user still processing
        return HttpResponse("<message>Loading all the games for user...</message>", content_type="application/xml")
    else:
        return HttpResponse(user.xml, content_type="application/xml")
