from django.db import models
from django.conf import settings
from django.utils import timezone


class WalletTransaction(models.Model):
	class Types(models.TextChoices):
		TOPUP = 'TOPUP'
		PAYMENT_RELEASE = 'PAYMENT_RELEASE'
		SUBSCRIPTION = 'SUBSCRIPTION'

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet_transactions')
	tx_type = models.CharField(max_length=32, choices=Types.choices)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	reference = models.CharField(max_length=64, blank=True)
	created_at = models.DateTimeField(default=timezone.now)


class LipanaTransaction(models.Model):
	class Status(models.TextChoices):
		PENDING = 'PENDING'
		SUCCESS = 'SUCCESS'
		FAILED = 'FAILED'

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lipana_transactions')
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	purpose = models.CharField(max_length=32)  # 'WALLET' or 'SUBSCRIPTION'
	reference = models.CharField(max_length=64, unique=True)
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
	created_at = models.DateTimeField(default=timezone.now)
	processed = models.BooleanField(default=False)

# Create your models here.
