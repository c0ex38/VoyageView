from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from backend.models import EmailVerification
from django.utils.timezone import now
from datetime import timedelta
from rest_framework.permissions import AllowAny


class ResendVerificationCodeAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        try:
            email_verification = EmailVerification.objects.get(user=user)

            # Doğrulama kodunun süresi dolmuşsa yeni kod oluştur
            if email_verification.created_at + timedelta(minutes=15) < now():
                email_verification.verification_code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                email_verification.created_at = now()
                email_verification.save()

            # Doğrulama kodunu e-posta ile gönder
            send_mail(
                subject="Verify Your Email",
                message=f"Your verification code is {email_verification.verification_code}.",
                from_email="your-email@example.com",
                recipient_list=[email],
            )

        except EmailVerification.DoesNotExist:
            # Kullanıcı için yeni bir doğrulama kaydı oluştur
            verification_code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            EmailVerification.objects.create(user=user, verification_code=verification_code)

            # Doğrulama kodunu e-posta ile gönder
            send_mail(
                subject="Verify Your Email",
                message=f"Your verification code is {verification_code}.",
                from_email="your-email@example.com",
                recipient_list=[email],
            )

        return Response({"message": "Verification code sent successfully."}, status=status.HTTP_200_OK)
