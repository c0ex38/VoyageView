from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.crypto import get_random_string
from rest_framework import status
from backend.models import EmailVerification
from django.utils.timezone import now
from datetime import timedelta


class RegisterUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data

        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

        if not username or not password or not email:
            return Response({"error": "Username, password, and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Kullanıcı oluşturma
        user = User.objects.create_user(username=username, password=password, email=email)

        # Doğrulama kodu üretimi
        verification_code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

        try:
            # Veritabanında sakla
            EmailVerification.objects.create(user=user, verification_code=verification_code)

            # E-posta gönderimi
            send_mail(
                subject="Verify Your Email",
                message=f"Your verification code is {verification_code}.",
                from_email="your-email@example.com",
                recipient_list=[email],
            )
        except Exception as e:
            user.delete()  # Hata durumunda kullanıcıyı sil
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "User registered successfully. Please verify your email.",
            "user_id": user.id,
        }, status=status.HTTP_201_CREATED)
