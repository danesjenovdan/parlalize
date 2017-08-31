from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parlalize.settings')

app = Celery('parlalize')
app.config_from_object('django.conf:settings', namespace='CELERYPARLALIZE')
app.autodiscover_tasks()
