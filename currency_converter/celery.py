from __future__ import absolute_import

import os
from celery import Celery

# Indicate Celery to use the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'currency_converter.settings')

app = Celery('currency_converter')
app.config_from_object('django.conf:settings')
# This line will tell Celery to autodiscover all your tasks.py that are in your app folders
app.autodiscover_tasks(['converter_app'])
