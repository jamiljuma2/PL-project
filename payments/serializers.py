from rest_framework import serializers
from accounts.models import Wallet
from .models import WalletTransaction, LipanaTransaction


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["balance", "updated_at"]


class WalletTopupSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class LipanaTxSerializer(serializers.ModelSerializer):
    class Meta:
        model = LipanaTransaction
        fields = ["reference", "amount", "purpose", "status", "processed", "created_at"]