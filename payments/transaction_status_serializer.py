from rest_framework import serializers
from .models import WalletTransaction, LipanaTransaction, Withdrawal

class TransactionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LipanaTransaction
        fields = ["reference", "amount", "purpose", "status", "processed", "created_at"]
