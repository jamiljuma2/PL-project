from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils.crypto import get_random_string
from accounts.models import Wallet
from accounts.permissions import IsAdminRole, IsStudent
from .models import WalletTransaction, LipanaTransaction, Withdrawal
from .serializers import WalletSerializer, WalletTopupSerializer, LipanaTxSerializer, WithdrawalSerializer
from rest_framework.permissions import BasePermission

# Permission: IsWriter
class IsWriter(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'WRITER'


# Writer requests withdrawal
class WithdrawalRequestView(APIView):
    permission_classes = [IsAuthenticated, IsWriter]

    def post(self, request):
        amount = request.data.get('amount')
        if not amount:
            return Response({"detail": "Amount required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount = float(amount)
        except Exception:
            return Response({"detail": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        wallet = getattr(request.user, 'wallet', None)
        if not wallet or wallet.balance < amount:
            return Response({"detail": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            withdrawal = Withdrawal.objects.create(user=request.user, amount=amount)
            wallet.balance -= amount
            wallet.save(update_fields=["balance"])
        return Response(WithdrawalSerializer(withdrawal).data, status=status.HTTP_201_CREATED)


# Admin approves/rejects withdrawal
class WithdrawalAdminActionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, pk):
        action = request.data.get('action')
        note = request.data.get('note', '')
        try:
            withdrawal = Withdrawal.objects.get(pk=pk)
        except Withdrawal.DoesNotExist:
            return Response({"detail": "Withdrawal not found"}, status=status.HTTP_404_NOT_FOUND)
        if action == 'approve':
            withdrawal.approve(admin_user=request.user, note=note)
            return Response({"detail": "Withdrawal approved"})
        elif action == 'reject':
            withdrawal.reject(admin_user=request.user, note=note)
            # Refund to wallet
            wallet = getattr(withdrawal.user, 'wallet', None)
            if wallet:
                wallet.balance += withdrawal.amount
                wallet.save(update_fields=["balance"])
            return Response({"detail": "Withdrawal rejected and refunded"})
        else:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


# List withdrawals for user (writer)
class WithdrawalListView(APIView):
    permission_classes = [IsAuthenticated, IsWriter]

    def get(self, request):
        withdrawals = Withdrawal.objects.filter(user=request.user).order_by('-requested_at')
        return Response(WithdrawalSerializer(withdrawals, many=True).data)


# List all withdrawals for admin
class WithdrawalAdminListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        withdrawals = Withdrawal.objects.all().order_by('-requested_at')
        return Response(WithdrawalSerializer(withdrawals, many=True).data)
from .services import trigger_stk_push
from django.conf import settings
import hmac
import hashlib


class WalletView(APIView):
    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return Response(WalletSerializer(wallet).data)


class WalletTopupView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request):
        ser = WalletTopupSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        amount = ser.validated_data['amount']
        data = trigger_stk_push(request.user.id, amount, 'WALLET')
        ref = data.get('reference') or get_random_string(12)
        LipanaTransaction.objects.create(user=request.user, amount=amount, purpose='WALLET', reference=ref)
        return Response({"detail": "STK push triggered", "reference": ref})


class LipanaCallbackView(APIView):
    permission_classes = []

    def post(self, request):
        # Basic authenticity check using HMAC of body
        signature = request.headers.get('X-Lipana-Signature', '')
        body_bytes = request.body or b''
        expected = hmac.new(settings.LIPANA_CALLBACK_SECRET.encode('utf-8'), body_bytes, hashlib.sha256).hexdigest()
        if not signature or signature != expected:
            return Response({"detail": "Invalid signature"}, status=status.HTTP_403_FORBIDDEN)

        ref = request.data.get('reference')
        status_str = request.data.get('status')
        amount = request.data.get('amount')
        tx = LipanaTransaction.objects.filter(reference=ref).first()
        if not tx:
            return Response({"detail": "Unknown reference"}, status=status.HTTP_404_NOT_FOUND)
        if tx.processed:
            return Response({"detail": "Already processed"})

        with transaction.atomic():
            tx.status = 'SUCCESS' if status_str == 'SUCCESS' else 'FAILED'
            tx.processed = True
            tx.save(update_fields=['status', 'processed'])
            if tx.status == 'SUCCESS':
                wallet, _ = Wallet.objects.get_or_create(user=tx.user)
                wallet.balance = wallet.balance + tx.amount
                wallet.save(update_fields=['balance'])
                WalletTransaction.objects.create(user=tx.user, tx_type='TOPUP', amount=tx.amount, reference=tx.reference)
        return Response({"detail": "Callback handled"})


class ReleasePaymentView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request):
        # expects writer_id and amount
        writer_id = request.data.get('writer_id')
        amount = request.data.get('amount')
        if not writer_id or not amount:
            return Response({"detail": "writer_id and amount required"}, status=status.HTTP_400_BAD_REQUEST)
        wallet, _ = Wallet.objects.get_or_create(user_id=writer_id)
        with transaction.atomic():
            wallet.balance = wallet.balance + amount
            wallet.save(update_fields=['balance'])
            WalletTransaction.objects.create(user_id=writer_id, tx_type='PAYMENT_RELEASE', amount=amount)
        return Response({"detail": "Payment released"})


class EarningsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Sum
        total = (
            WalletTransaction.objects.filter(user=request.user, tx_type='PAYMENT_RELEASE')
            .aggregate(total_amount=Sum('amount'))
            .get('total_amount')
        ) or 0
        return Response({"total": total})
