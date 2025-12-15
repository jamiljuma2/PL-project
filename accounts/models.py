from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class User(AbstractUser):
	class Roles(models.TextChoices):
		STUDENT = "STUDENT", _("Student")
		WRITER = "WRITER", _("Writer")
		ADMIN = "ADMIN", _("Admin")

	role = models.CharField(max_length=16, choices=Roles.choices, default=Roles.STUDENT)
	# is_verified removed

	def __str__(self):
		return f"{self.username} ({self.role})"


class Wallet(models.Model):
	user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='wallet')
	balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Wallet<{self.user_id}>: {self.balance}"


class Rating(models.Model):
	user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='rating')
	points = models.IntegerField(default=0)
	badge = models.CharField(max_length=16, default="Bronze")

	def recalc_badge(self):
		p = self.points
		if p <= 10:
			self.badge = "Bronze"
		elif p <= 30:
			self.badge = "Silver"
		elif p <= 60:
			self.badge = "Gold"
		else:
			self.badge = "Platinum"

	def add_points(self, pts: int):
		self.points = (self.points or 0) + pts
		self.recalc_badge()
		self.save(update_fields=["points", "badge"])

	def __str__(self):
		return f"Rating<{self.user_id}>: {self.points} ({self.badge})"


class Notification(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
	title = models.CharField(max_length=200)
	body = models.TextField()
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"Notif<{self.id}> to {self.user_id}: {self.title}"




class PasswordReset(models.Model):
	user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
	token = models.CharField(max_length=64, unique=True)
	is_used = models.BooleanField(default=False)
	created_at = models.DateTimeField(default=timezone.now)

# Create your models here.
