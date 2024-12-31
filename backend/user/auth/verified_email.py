from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from backend.models import EmailVerification
from django.utils.timezone import now
from datetime import timedelta 
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User

class VerifyEmailAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Kullanıcının e-posta doğrulama kodunu doğrular.
        - Kullanıcı ID ve doğrulama kodu alınır.
        - Kod süresi kontrol edilir. Süresi dolmuşsa, kullanıcıya yeni bir kod talep etmesi istenir.
        - Kod doğruysa, kullanıcının e-posta doğrulaması yapılır.
        """
        data = request.data

        user_id = data.get("user_id")
        verification_code = data.get("verification_code")

        if not user_id or not verification_code:
            return Response({"error": "Kullanıcı ID'si ve doğrulama kodu gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Veritabanında doğrulama kaydını bulmaya çalışıyoruz
            email_verification = EmailVerification.objects.get(user_id=user_id)
        except EmailVerification.DoesNotExist:
            return Response({"error": "Doğrulama kaydı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

        # Kod süresini kontrol ediyoruz
        if email_verification.created_at + timedelta(minutes=15) < now():
            # Kod süresi dolmuşsa kaydı siliyoruz ve hata mesajı döndürüyoruz
            email_verification.delete()
            return Response({"error": "Doğrulama kodu süresi dolmuş. Lütfen yeni bir kod talep edin."}, status=status.HTTP_400_BAD_REQUEST)

        # Kod doğrulaması yapıyoruz
        if email_verification.verification_code == verification_code:
            # Kod doğruysa, kullanıcının e-posta doğrulamasını yapıyoruz
            email_verification.user.profile.is_email_verified = True
            email_verification.user.profile.save()
            email_verification.delete()

            return Response({"message": "E-posta başarıyla doğrulandı."}, status=status.HTTP_200_OK)

        return Response({"error": "Geçersiz doğrulama kodu."}, status=status.HTTP_400_BAD_REQUEST)
