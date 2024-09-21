from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

@shared_task
def send_async_mail(subject, message, recipient_list, html_message):
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, html_message=html_message)
