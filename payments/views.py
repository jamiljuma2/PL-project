from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils.crypto import get_random_string
from accounts.models import Wallet
from accounts.permissions import IsAdminRole, IsStudent
from .transaction_status_serializer import TransactionStatusSerializer

# API endpoint for frontend to poll transaction status
class TransactionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, reference):
        try:
            tx = LipanaTransaction.objects.get(reference=reference, user=request.user)
        except LipanaTransaction.DoesNotExist:
            return Response({"detail": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(TransactionStatusSerializer(tx).data)
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
        ser = WithdrawalSerializer(data=request.data)
        if not ser.is_valid():
            return Response({"errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)
        amount = ser.validated_data.get('amount')
        if amount is None or amount <= 0:
            return Response({"detail": "Amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)
        wallet = getattr(request.user, 'wallet', None)
        if not wallet or wallet.balance < amount:
            return Response({"detail": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            withdrawal = Withdrawal.objects.create(user=request.user, amount=amount)
            wallet.balance -= amount
            wallet.save(update_fields=["balance"])
        return Response({"withdrawal": WithdrawalSerializer(withdrawal).data}, status=status.HTTP_201_CREATED)


# Admin approves/rejects withdrawal
class WithdrawalAdminActionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, pk):
        action = request.data.get('action')
        note = request.data.get('note', '')
        if action not in ['approve', 'reject']:
            return Response({"detail": "Invalid action. Must be 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            withdrawal = Withdrawal.objects.get(pk=pk)
        except Withdrawal.DoesNotExist:
            return Response({"detail": "Withdrawal not found."}, status=status.HTTP_404_NOT_FOUND)
        if withdrawal.status != withdrawal.Status.PENDING:
            return Response({"detail": "Withdrawal already processed."}, status=status.HTTP_400_BAD_REQUEST)
        if action == 'approve':
            withdrawal.approve(admin_user=request.user, note=note)
            return Response({"detail": "Withdrawal approved."}, status=status.HTTP_200_OK)
        elif action == 'reject':
            withdrawal.reject(admin_user=request.user, note=note)
            wallet = getattr(withdrawal.user, 'wallet', None)
            if wallet:
                wallet.balance += withdrawal.amount
                wallet.save(update_fields=["balance"])
            return Response({"detail": "Withdrawal rejected and refunded."}, status=status.HTTP_200_OK)


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
        from django.utils import timezone
        ser = WalletTopupSerializer(data=request.data)
        if not ser.is_valid():
            return Response({"errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)
        amount = ser.validated_data['amount']
        if amount <= 0:
            return Response({"detail": "Amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)
        data = trigger_stk_push(request.user.id, amount, 'WALLET')
        ref = data.get('reference') or get_random_string(12)
        code = data.get('code')
        message = data.get('message')
        LipanaTransaction.objects.create(
            user=request.user,
            amount=amount,
            purpose='WALLET',
            reference=ref,
            stk_push_code=code,
            stk_push_message=message,
            stk_push_at=timezone.now(),
        )
        return Response({"detail": "STK push triggered.", "reference": ref, "code": code, "message": message}, status=status.HTTP_201_CREATED)


class LipanaCallbackView(APIView):
    permission_classes = []

    def post(self, request):
        from django.utils import timezone
        # Basic authenticity check using HMAC of body
        signature = request.headers.get('X-Lipana-Signature', '')
        body_bytes = request.body or b''
        expected = hmac.new(settings.LIPANA_CALLBACK_SECRET.encode('utf-8'), body_bytes, hashlib.sha256).hexdigest()
        if not signature or signature != expected:
            return Response({"detail": "Invalid signature"}, status=status.HTTP_403_FORBIDDEN)

        ref = request.data.get('reference')
        status_str = request.data.get('status')
        amount = request.data.get('amount')
        code = request.data.get('code')
        message = request.data.get('message')
        tx = LipanaTransaction.objects.filter(reference=ref).first()
        if not tx:
            return Response({"detail": "Unknown reference"}, status=status.HTTP_404_NOT_FOUND)
        if tx.processed:
            return Response({"detail": "Already processed"})

        with transaction.atomic():
            tx.status = 'SUCCESS' if status_str == 'SUCCESS' else 'FAILED'
            tx.processed = True
            tx.stk_push_code = code or tx.stk_push_code
            tx.stk_push_message = message or tx.stk_push_message
            tx.callback_at = timezone.now()
            tx.save(update_fields=['status', 'processed', 'stk_push_code', 'stk_push_message', 'callback_at'])
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
