from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from backend.models import EmailVerification
from django.utils.timezone import now
from datetime import timedelta  # timedelta burada import ediliyor
from rest_framework.permissions import AllowAny


class VerifyEmailAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        user_id = data.get("user_id")
        verification_code = data.get("verification_code")

        if not user_id or not verification_code:
            return Response({"error": "User ID and verification code are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            email_verification = EmailVerification.objects.get(user_id=user_id)
        except EmailVerification.DoesNotExist:
            return Response({"error": "Verification record not found."}, status=status.HTTP_404_NOT_FOUND)

        # Kod süresini kontrol et
        if email_verification.created_at + timedelta(minutes=15) < now():
            email_verification.delete()
            return Response({"error": "Verification code expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        # Kod doğrulama
        if email_verification.verification_code == verification_code:
            email_verification.user.profile.is_email_verified = True
            email_verification.user.profile.save()
            email_verification.delete()

            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)
