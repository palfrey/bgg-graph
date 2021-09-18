import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bgg_graph.settings')
app = Celery('bgg_graph')
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()