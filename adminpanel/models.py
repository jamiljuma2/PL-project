from django.db import models
from django.conf import settings
from django.utils import timezone


class AdminActionLog(models.Model):
	admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	action = models.CharField(max_length=64)
	target = models.CharField(max_length=64)
	details = models.TextField(blank=True)
	created_at = models.DateTimeField(default=timezone.now)

# Create your models here.
