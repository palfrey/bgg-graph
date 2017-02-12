from django.shortcuts import render
import requests
from django.http import HttpResponse
from models import *
from tasks import update_user

def user(request, name):
    users = User.objects.filter(name=name)
    update_user.delay(name)
    if not users.exists():
        raise Exception
    else:
        raise Exception
