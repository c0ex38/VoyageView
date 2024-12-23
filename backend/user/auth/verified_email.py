from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from backend.models import EmailVerification
from django.utils.timezone import now
from datetime import timedelta 
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User

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


class GetUserIdAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        username = request.query_params.get('username')
        if not username:
            return Response({"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
            return Response({"user_id": user.id}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
