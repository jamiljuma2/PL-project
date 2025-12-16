from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from .serializers import RegisterSerializer, UserSerializer, WalletSerializer, NotificationSerializer, RatingSerializer
from .models import PasswordReset
from .tasks import send_password_reset_email

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LogoutView(APIView):
    def post(self, request):
        try:
            refresh = request.data.get("refresh")
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({"detail": "Logged out"})
        except Exception:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "If the email exists, a reset will be sent."})
        token = get_random_string(length=48)
        PasswordReset.objects.create(user=user, token=token)
        # Send password reset email async
        try:
            send_password_reset_email.delay(user.id, token)
        except Exception:
            pass
        return Response({"detail": "Password reset token created"})



# Password Reset Confirm View
from .serializers import PasswordResetConfirmSerializer

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password has been reset successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class MeView(APIView):
    def get(self, request):
        data = {
            "user": UserSerializer(request.user).data,
        }
        if hasattr(request.user, 'wallet'):
            data["wallet"] = WalletSerializer(request.user.wallet).data
        if getattr(request.user, 'role', None) == 'WRITER' and hasattr(request.user, 'rating'):
            data["rating"] = RatingSerializer(request.user.rating).data
        return Response(data)


class MyNotificationsView(APIView):
    def get(self, request):
        qs = request.user.notifications.order_by('-created_at')[:100]
        return Response(NotificationSerializer(qs, many=True).data)


class MyRatingView(APIView):
    def get(self, request):
        if getattr(request.user, 'role', None) != 'WRITER' or not hasattr(request.user, 'rating'):
            return Response({"detail": "No rating"}, status=status.HTTP_404_NOT_FOUND)
        return Response(RatingSerializer(request.user.rating).data)
