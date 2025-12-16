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


class Withdrawal(models.Model):
	# Optionally add admin_user field for tracking who approved/rejected
	admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_withdrawals')
	class Status(models.TextChoices):
		PENDING = 'PENDING', 'Pending'
		APPROVED = 'APPROVED', 'Approved'
		REJECTED = 'REJECTED', 'Rejected'

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='withdrawals')
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
	requested_at = models.DateTimeField(default=timezone.now)
	processed_at = models.DateTimeField(null=True, blank=True)
	admin_note = models.TextField(blank=True)

	def approve(self, admin_user=None, note=None):
		if self.status != self.Status.PENDING:
			raise ValueError('Withdrawal already processed.')
		self.status = self.Status.APPROVED
		self.processed_at = timezone.now()
		if note:
			self.admin_note = note
		self.save(update_fields=["status", "processed_at", "admin_note"])

	def reject(self, admin_user=None, note=None):
		if self.status != self.Status.PENDING:
			raise ValueError('Withdrawal already processed.')
		self.status = self.Status.REJECTED
		self.processed_at = timezone.now()
		if note:
			self.admin_note = note
		self.save(update_fields=["status", "processed_at", "admin_note"])

	def __str__(self):
		return f"Withdrawal<{self.id}>: {self.user} - {self.amount} ({self.status})"
