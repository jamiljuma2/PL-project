from django.contrib import admin

from .models import User, Wallet, Rating, Notification



class WalletInline(admin.StackedInline):
	model = Wallet
	can_delete = False
	readonly_fields = ("balance", "updated_at")
	extra = 0

class RatingInline(admin.StackedInline):
	model = Rating
	can_delete = False
	readonly_fields = ("points", "badge")
	extra = 0

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("id", "username", "email", "role", "is_active")
	list_filter = ("role", "is_active")
	search_fields = ("username", "email")
	inlines = [WalletInline, RatingInline]



from django.utils.html import format_html
from django.urls import reverse

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
	list_display = ("user_link", "balance", "updated_at")

	def user_link(self, obj):
		url = reverse("admin:accounts_user_change", args=[obj.user.id])
		return format_html('<a href="{}">{}</a>', url, obj.user)
	user_link.short_description = "User"



@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
	list_display = ("user_link", "points", "badge")

	def user_link(self, obj):
		url = reverse("admin:accounts_user_change", args=[obj.user.id])
		return format_html('<a href="{}">{}</a>', url, obj.user)
	user_link.short_description = "User"



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("user_link", "title", "is_read", "created_at")

	def user_link(self, obj):
		url = reverse("admin:accounts_user_change", args=[obj.user.id])
		return format_html('<a href="{}">{}</a>', url, obj.user)
	user_link.short_description = "User"
