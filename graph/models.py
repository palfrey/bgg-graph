from __future__ import unicode_literals

from django.db import models

class User(models.Model):
    name = models.CharField(primary_key=True, max_length=200)
    xml = models.TextField()
