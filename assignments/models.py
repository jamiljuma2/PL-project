from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


def student_upload_path(instance, filename):
	return f"student/{instance.assignment_id}/{uuid.uuid4()}"


def writer_upload_path(instance, filename):
	return f"writer/{instance.assignment_id}/{uuid.uuid4()}"


def _validate_file(file_obj):
	max_mb = getattr(settings, 'MAX_FILE_SIZE_MB', 20)
	size = getattr(file_obj, 'size', 0)
	if size and size > max_mb * 1024 * 1024:
		raise ValidationError(f"File too large. Max {max_mb} MB")
	name = getattr(file_obj, 'name', '')
	ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
	allowed = set(getattr(settings, 'ALLOWED_FILE_EXTENSIONS', []))
	if allowed and ext not in allowed:
		raise ValidationError(f"Unsupported file type: .{ext}")


class Assignment(models.Model):
	class Status(models.TextChoices):
		PENDING_APPROVAL = 'PENDING_APPROVAL'
		APPROVED = 'APPROVED'
		IN_PROGRESS = 'IN_PROGRESS'
		COMPLETED = 'COMPLETED'
		REJECTED = 'REJECTED'

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignments')
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING_APPROVAL)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"Assignment<{self.id}> {self.title} [{self.status}]"


class AssignmentFile(models.Model):
	assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='files')
	file = models.FileField(upload_to=student_upload_path)
	uploaded_at = models.DateTimeField(default=timezone.now)
	size_bytes = models.BigIntegerField(default=0)

	def save(self, *args, **kwargs):
		if self.file:
			_validate_file(self.file)
		super().save(*args, **kwargs)
		try:
			self.size_bytes = self.file.size
		except Exception:
			pass
		super().save(update_fields=['size_bytes'])


class TaskClaim(models.Model):
	assignment = models.OneToOneField(Assignment, on_delete=models.CASCADE, related_name='claim')
	writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claims')
	claimed_at = models.DateTimeField(default=timezone.now)


class Submission(models.Model):
	class Status(models.TextChoices):
		PENDING_REVIEW = 'PENDING_REVIEW'
		APPROVED = 'APPROVED'
		REJECTED = 'REJECTED'

	assignment = models.OneToOneField(Assignment, on_delete=models.CASCADE, related_name='submission')
	writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
	file = models.FileField(upload_to=writer_upload_path)
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING_REVIEW)
	notes = models.TextField(blank=True)
	uploaded_at = models.DateTimeField(default=timezone.now)

	def save(self, *args, **kwargs):
		if self.file:
			_validate_file(self.file)
		super().save(*args, **kwargs)

# Create your models here.
