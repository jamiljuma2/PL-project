from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("APPROVE_WITHDRAWAL", "Approve Withdrawal"),
        ("REJECT_WITHDRAWAL", "Reject Withdrawal"),
        ("CREATE_WITHDRAWAL", "Create Withdrawal"),
        # Add more as needed
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    target_id = models.CharField(max_length=64, blank=True)  # e.g., withdrawal id
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp}: {self.user} {self.action} {self.target_id}"
