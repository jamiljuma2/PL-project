from django.contrib import admin
from .models import User, Wallet, Rating, Notification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("id", "username", "email", "role", "is_active")
	list_filter = ("role", "is_active")


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
	list_display = ("user", "balance", "updated_at")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
	list_display = ("user", "points", "badge")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("user", "title", "is_read", "created_at")
