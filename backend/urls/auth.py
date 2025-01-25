from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from backend.auth.register import RegisterUserAPIView
from backend.auth.verified_email import VerifyEmailAPIView
from backend.auth.resend_email import ResendVerificationCodeAPIView
from backend.auth.login import LoginUserAPIView
from backend.auth.logout import LogoutUserAPIView

from backend.auth.password_reset import PasswordResetRequestAPIView, PasswordResetConfirmAPIView
from backend.auth.password_update import PasswordUpdateAPIView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('verify-email/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('resend-code/', ResendVerificationCodeAPIView.as_view(), name='resend-code'),
    path('login/', LoginUserAPIView.as_view(), name='login'),
    path('logout/', LogoutUserAPIView.as_view(), name='logout'),
    path('password-reset/', PasswordResetRequestAPIView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
    path('password-update/', PasswordUpdateAPIView.as_view(), name='password-update'),
]
