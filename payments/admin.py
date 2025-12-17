from django.contrib import admin
from .models import WalletTransaction, LipanaTransaction, Withdrawal
from .audit import AuditLog
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
	list_display = ("timestamp", "user", "action", "target_id", "details")
	search_fields = ("user__username", "action", "target_id", "details")
	list_filter = ("action", "timestamp")


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
	list_display = ("user", "amount", "status", "requested_at", "processed_at")
	list_filter = ("status", "requested_at", "processed_at")
	search_fields = ("user__username", "user__email", "amount", "status")
	readonly_fields = ("user", "amount", "requested_at", "status", "processed_at", "admin_note")

	actions = ["approve_selected", "reject_selected"]

	def approve_selected(self, request, queryset):
		if not request.user.groups.filter(name='Finance Admin').exists():
			self.message_user(request, "Only Finance Admin can approve withdrawals.", level='error')
			return
		count = 0
		for obj in queryset:
			if obj.status == obj.Status.PENDING:
				obj.approve(admin_user=request.user)
				AuditLog.objects.create(
					user=request.user,
					action="APPROVE_WITHDRAWAL",
					target_id=str(obj.id),
					details=f"Approved withdrawal of {obj.amount} for user {obj.user_id}"
				)
				count += 1
		self.message_user(request, f"{count} withdrawals approved.")
	approve_selected.short_description = "Approve selected withdrawals"

	def reject_selected(self, request, queryset):
		if not request.user.groups.filter(name='Finance Admin').exists():
			self.message_user(request, "Only Finance Admin can reject withdrawals.", level='error')
			return
		count = 0
		for obj in queryset:
			if obj.status == obj.Status.PENDING:
				obj.reject(admin_user=request.user)
				AuditLog.objects.create(
					user=request.user,
					action="REJECT_WITHDRAWAL",
					target_id=str(obj.id),
					details=f"Rejected withdrawal of {obj.amount} for user {obj.user_id}"
				)
				count += 1
		self.message_user(request, f"{count} withdrawals rejected.")
	reject_selected.short_description = "Reject selected withdrawals"




@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
	list_display = ("user", "tx_type", "amount", "reference", "created_at")
	list_filter = ("tx_type", "created_at")
	search_fields = ("user__username", "user__email", "tx_type", "reference", "amount")
	readonly_fields = ("user", "tx_type", "amount", "reference", "created_at")

	actions = ["approve_selected", "reject_selected"]

	def approve_selected(self, request, queryset):
		count = 0
		for obj in queryset:
			if hasattr(obj, 'status') and hasattr(obj, 'approve') and obj.status == obj.Status.PENDING:
				obj.approve(admin_user=request.user)
				count += 1
		self.message_user(request, f"{count} transactions approved.")
	approve_selected.short_description = "Approve selected transactions"

	def reject_selected(self, request, queryset):
		count = 0
		for obj in queryset:
			if hasattr(obj, 'status') and hasattr(obj, 'reject') and obj.status == obj.Status.PENDING:
				obj.reject(admin_user=request.user)
				count += 1
		self.message_user(request, f"{count} transactions rejected.")
	reject_selected.short_description = "Reject selected transactions"




@admin.register(LipanaTransaction)
class LipanaTransactionAdmin(admin.ModelAdmin):
	list_display = ("user", "purpose", "amount", "reference", "status", "processed", "created_at")
	list_filter = ("status", "purpose", "processed", "created_at")
	search_fields = ("user__username", "user__email", "purpose", "reference", "amount", "status")

	actions = ["approve_selected", "reject_selected"]

	def approve_selected(self, request, queryset):
		count = 0
		for obj in queryset:
			if hasattr(obj, 'status') and hasattr(obj, 'approve') and obj.status == obj.Status.PENDING:
				obj.status = obj.Status.SUCCESS
				obj.processed = True
				obj.save(update_fields=["status", "processed"])
				count += 1
		self.message_user(request, f"{count} transactions approved.")
	approve_selected.short_description = "Approve selected transactions"

	def reject_selected(self, request, queryset):
		count = 0
		for obj in queryset:
			if hasattr(obj, 'status') and obj.status == obj.Status.PENDING:
				obj.status = obj.Status.FAILED
				obj.processed = True
				obj.save(update_fields=["status", "processed"])
				count += 1
		self.message_user(request, f"{count} transactions rejected.")
	reject_selected.short_description = "Reject selected transactions"
