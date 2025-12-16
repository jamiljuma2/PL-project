from django.urls import path
from .views import WalletView, WalletTopupView, LipanaCallbackView, ReleasePaymentView, EarningsView, WithdrawalRequestView, WithdrawalAdminActionView, WithdrawalListView, WithdrawalAdminListView

urlpatterns = [
    path('wallet/', WalletView.as_view(), name='wallet-get'),
    path('wallet/topup', WalletTopupView.as_view(), name='wallet-topup'),
    path('payments/lipana/callback', LipanaCallbackView.as_view(), name='lipana-callback'),
    path('admin/payments/release', ReleasePaymentView.as_view(), name='admin-payments-release'),
    path('earnings/', EarningsView.as_view(), name='earnings'),

    # Withdrawals
    path('withdrawals/', WithdrawalListView.as_view(), name='withdrawal-list'),
    path('withdrawals/request', WithdrawalRequestView.as_view(), name='withdrawal-request'),
    path('admin/withdrawals/', WithdrawalAdminListView.as_view(), name='admin-withdrawal-list'),
    path('admin/withdrawals/<int:pk>/action', WithdrawalAdminActionView.as_view(), name='admin-withdrawal-action'),
]