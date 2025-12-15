from django.urls import path
from .views import SubscriptionPayView, SubscriptionStatusView

urlpatterns = [
    path('subscriptions/pay', SubscriptionPayView.as_view(), name='subscriptions-pay'),
    path('subscriptions/status', SubscriptionStatusView.as_view(), name='subscriptions-status'),
]