from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from django.utils.crypto import get_random_string
from backend.models import EmailVerification
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now

class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Şifre sıfırlama talebi alır.
        - Kullanıcıya sıfırlama kodu gönderir.
        - Kod, veritabanına kaydedilir veya mevcut kaydın doğrulama kodu güncellenir.
        """
        email = request.data.get("email")

        if not email:
            return Response({"error": "E-posta gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Bu e-posta ile kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

        # Rastgele bir şifre sıfırlama kodu oluşturuluyor
        reset_code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

        # Kullanıcının mevcut doğrulama kaydını bulup güncellenmesi için kontrol
        try:
            email_verification = EmailVerification.objects.get(user=user)
            email_verification.verification_code = reset_code
            email_verification.created_at = now()  # Yeni zamanla güncelle
            email_verification.save()
        except EmailVerification.DoesNotExist:
            # Eğer doğrulama kaydı yoksa, yeni bir kayıt oluşturulur
            EmailVerification.objects.create(user=user, verification_code=reset_code)

        # E-posta ile sıfırlama kodunu gönderiyoruz
        try:
            send_mail(
                subject="Şifre Sıfırlama Talebi",
                message=f"Şifre sıfırlama kodunuz: {reset_code}.",
                from_email="your-email@example.com",
                recipient_list=[email],
            )
        except BadHeaderError:
            return Response({"error": "E-posta gönderirken geçersiz başlık bulundu."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"E-posta gönderilirken bir hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Şifre sıfırlama kodu e-posta ile gönderildi."}, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Şifre sıfırlama kodunu doğrular ve yeni şifreyi kaydeder.
        - Kullanıcıdan e-posta, sıfırlama kodu ve yeni şifre alır.
        - Geçerli bir sıfırlama kodu kontrolü yapılır.
        """
        email = request.data.get("email")
        reset_code = request.data.get("reset_code")
        new_password = request.data.get("new_password")

        if not email or not reset_code or not new_password:
            return Response({"error": "E-posta, sıfırlama kodu ve yeni şifre gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Bu e-posta ile kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

        try:
            email_verification = EmailVerification.objects.get(user=user, verification_code=reset_code)
        except EmailVerification.DoesNotExist:
            return Response({"error": "Geçersiz veya süresi dolmuş sıfırlama kodu."}, status=status.HTTP_400_BAD_REQUEST)

        # Şifreyi sıfırlıyoruz
        user.set_password(new_password)
        user.save()

        # Kullanılan sıfırlama kodunu silebiliriz
        email_verification.delete()

        return Response({"message": "Şifre başarıyla sıfırlandı."}, status=status.HTTP_200_OK)
