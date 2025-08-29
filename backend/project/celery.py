# backend/core/celery.py
import os
from celery import Celery
from django.core.mail import send_mail

# Define Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')
app.config_from_object('django.conf:settings', namespace='CELERY')


@app.task
def debug_task():
    print('Hello World')

def send_email_task(subject, message, recipient_list, email_from):
    #send email if the configuration is correct
    send_mail(subject, message, email_from, recipient_list)
    return True


#Load tasks modules from all registered Django apps
app.autodiscover_tasks()
