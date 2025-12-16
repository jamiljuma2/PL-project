from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .models import Wallet, Rating, Notification

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "is_active"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_verified = True  # Always verified since email verification is removed
        user.save()
        # Create related models
        Wallet.objects.create(user=user)
        if user.role == 'WRITER':
            Rating.objects.create(user=user)
        return user


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["balance", "updated_at"]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["points", "badge"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "body", "is_read", "created_at"]


# Password Reset Confirm Serializer
from .models import PasswordReset

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        token = attrs.get('token')
        try:
            reset_obj = PasswordReset.objects.get(token=token, is_used=False)
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError({'token': 'Invalid or used token.'})
        # Optionally: check token expiration (e.g., 1 hour)
        from django.utils import timezone
        if (timezone.now() - reset_obj.created_at).total_seconds() > 3600:
            raise serializers.ValidationError({'token': 'Token expired.'})
        attrs['reset_obj'] = reset_obj
        return attrs

    def save(self, **kwargs):
        reset_obj = self.validated_data['reset_obj']
        user = reset_obj.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        reset_obj.is_used = True
        reset_obj.save()
        return user