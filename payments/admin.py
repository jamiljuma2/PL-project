from django.contrib import admin
from .models import WalletTransaction, LipanaTransaction


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
	list_display = ("user", "tx_type", "amount", "reference", "created_at")
	readonly_fields = ("user", "tx_type", "amount", "reference", "created_at")


@admin.register(LipanaTransaction)
class LipanaTransactionAdmin(admin.ModelAdmin):
	list_display = ("user", "purpose", "amount", "reference", "status", "processed", "created_at")
	list_filter = ("status", "purpose")
