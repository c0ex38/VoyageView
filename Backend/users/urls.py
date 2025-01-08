from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, VerifyEmailView, ResendVerificationCodeView,
    PasswordResetRequestView, PasswordResetConfirmView, ProfileUpdateView,
    FollowUserView, UserStatisticsView, LogoutView, CheckFieldAvailabilityView,
    UserProfileView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification-code/', ResendVerificationCodeView.as_view(), name='resend_verification_code'),
    path('reset-password-request/', PasswordResetRequestView.as_view(), name='reset_password_request'),
    path('reset-password-confirm/', PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
    path('profile/', ProfileUpdateView.as_view(), name='profile_update'),
    path('<int:user_id>/follow/', FollowUserView.as_view(), name='follow_user'),
    path('statistics/', UserStatisticsView.as_view(), name='user_statistics'),
    path('check-availability/', CheckFieldAvailabilityView.as_view(), name='check_availability'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='user_profile'),
]