from celery import shared_task
from django.contrib.auth import get_user_model
from accounts.models import Notification

User = get_user_model()


@shared_task
def send_notification(user_id: int, title: str, body: str):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return "no-user"
    Notification.objects.create(user=user, title=title, body=body)
    return "created"