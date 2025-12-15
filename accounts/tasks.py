from celery import shared_task
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model

User = get_user_model()




@shared_task
def send_password_reset_email(user_id: int, token: str):
    user = User.objects.filter(id=user_id).first()
    if not user or not user.email:
        return "no-user-or-email"
    subject = "Password Reset"
    body = f"Hello {user.username},\n\nUse this token to reset your password: {token}\n\nIf you did not request this, please ignore."
    EmailMessage(subject, body, to=[user.email]).send()
    return "sent"