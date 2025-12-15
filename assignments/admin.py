from django.contrib import admin
from .models import Assignment, AssignmentFile, TaskClaim, Submission


@admin.action(description="Approve selected assignments")
def approve_assignments(modeladmin, request, queryset):
    queryset.update(status=Assignment.Status.APPROVED)


@admin.action(description="Reject selected assignments")
def reject_assignments(modeladmin, request, queryset):
    queryset.update(status=Assignment.Status.REJECTED)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "student", "status", "created_at")
    list_filter = ("status",)
    actions = [approve_assignments, reject_assignments]


@admin.register(AssignmentFile)
class AssignmentFileAdmin(admin.ModelAdmin):
    list_display = ("assignment", "uploaded_at", "size_bytes")


@admin.register(TaskClaim)
class TaskClaimAdmin(admin.ModelAdmin):
    list_display = ("assignment", "writer", "claimed_at")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "writer", "status", "uploaded_at")
    list_filter = ("status",)
