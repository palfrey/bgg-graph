from django.shortcuts import render
import requests
from django.http import HttpResponse
from models import *

def user(request, name):
    users = User.objects.filter(name=name)
    if not users.exists():
        url = "https://www.boardgamegeek.com/xmlapi2/collection?username=%s&subtype=boardgame&excludessubtype=boardgameexpansion" % name
        info = requests.get(url)
        User.objects.create(name=name, xml=info.text)
        return HttpResponse(info)
    else:
        return HttpResponse(users[0].xml)
