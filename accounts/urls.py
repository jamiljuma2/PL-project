from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, LogoutView, PasswordResetView, MeView, MyNotificationsView, MyRatingView, PasswordResetConfirmView

urlpatterns = [
    path('register', RegisterView.as_view(), name='auth-register'),
    path('login', TokenObtainPairView.as_view(), name='auth-login'),
    path('logout', LogoutView.as_view(), name='auth-logout'),
    path('refresh', TokenRefreshView.as_view(), name='auth-refresh'),
    path('password-reset', PasswordResetView.as_view(), name='auth-password-reset'),
    path('me', MeView.as_view(), name='auth-me'),
    path('notifications', MyNotificationsView.as_view(), name='auth-notifications'),
    path('ratings/me', MyRatingView.as_view(), name='ratings-me'),
    path('password-reset-confirm', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
]