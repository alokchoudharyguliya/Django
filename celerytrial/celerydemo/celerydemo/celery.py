import os
from celery import Celery
# set the default django settings module for the 'celery' program
os.environ.setdefault("DJANGO_SETTINGS_MODULE","celerydemo.settings")
app=Celery('celerydemo')

app.config_from_object("django.conf:settings",namespace="CELERY") # namespace means all the celery-related configuration keys should have a "CELERY_"  prefix
# load task modules from all registered django app configs
app.autodiscover_tasks()