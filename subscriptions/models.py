from django.db import models
from django.conf import settings
from django.utils import timezone


class Subscription(models.Model):
	class Plans(models.TextChoices):
		P2 = 'P2'  # $2 → 5 tasks/day
		P5 = 'P5'  # $5 → 9 tasks/day
		P10 = 'P10'  # $10 → Unlimited

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
	plan = models.CharField(max_length=8, choices=Plans.choices, default=Plans.P2)
	active = models.BooleanField(default=False)
	daily_count = models.IntegerField(default=0)
	daily_date = models.DateField(default=timezone.now)

	def reset_if_new_day(self):
		today = timezone.localdate()
		if self.daily_date != today:
			self.daily_date = today
			self.daily_count = 0

	def can_claim(self) -> bool:
		self.reset_if_new_day()
		if self.plan == self.Plans.P10:
			return True
		limit = 5 if self.plan == self.Plans.P2 else 9
		return self.daily_count < limit

	def register_claim(self):
		self.reset_if_new_day()
		self.daily_count += 1
		self.save(update_fields=['daily_date', 'daily_count'])

# Create your models here.
