from django.contrib import admin
from .models import AdminActionLog


@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
	list_display = ("admin", "action", "target", "created_at")
	readonly_fields = ("admin", "action", "target", "details", "created_at")
