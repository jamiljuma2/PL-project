from django.urls import path
from .views import WalletView, WalletTopupView, LipanaCallbackView, ReleasePaymentView, EarningsView

urlpatterns = [
    path('wallet/', WalletView.as_view(), name='wallet-get'),
    path('wallet/topup', WalletTopupView.as_view(), name='wallet-topup'),
    path('payments/lipana/callback', LipanaCallbackView.as_view(), name='lipana-callback'),
    path('admin/payments/release', ReleasePaymentView.as_view(), name='admin-payments-release'),
    path('earnings/', EarningsView.as_view(), name='earnings'),
]