# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-06 02:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0003_tree_node'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='processing_task',
            field=models.UUIDField(null=True),
        ),
    ]
