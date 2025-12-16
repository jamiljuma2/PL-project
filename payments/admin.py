from django.contrib import admin
from .models import WalletTransaction, LipanaTransaction, Withdrawal

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
	list_display = ("user", "amount", "status", "requested_at", "processed_at")
	list_filter = ("status",)
	search_fields = ("user__username",)
	readonly_fields = ("user", "amount", "requested_at", "status", "processed_at", "admin_note")


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
	list_display = ("user", "tx_type", "amount", "reference", "created_at")
	readonly_fields = ("user", "tx_type", "amount", "reference", "created_at")


@admin.register(LipanaTransaction)
class LipanaTransactionAdmin(admin.ModelAdmin):
	list_display = ("user", "purpose", "amount", "reference", "status", "processed", "created_at")
	list_filter = ("status", "purpose")
