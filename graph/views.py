from django.shortcuts import render
import requests
from django.http import HttpResponse
from models import *
import xml.etree.ElementTree as ET
import pprint

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
    items = []
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
        gameroot = ET.fromstring(xml.encode('utf-8'))
    return HttpResponse(pprint.pformat(sorted(items)))

