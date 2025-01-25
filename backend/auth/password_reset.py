# views/password_reset.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import send_mail, BadHeaderError
from rest_framework.permissions import AllowAny
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import check_password
from django.utils.timezone import now
from datetime import timedelta

from backend.models import EmailVerification, PasswordHistory
from backend.utils import validate_password_strength

class BasePasswordResetView(APIView):
    """Base class for password reset views with common utilities"""
    permission_classes = [AllowAny]
    PASSWORD_HISTORY_LIMIT = 5
    CODE_EXPIRY_MINUTES = 15
    RATE_LIMIT_MINUTES = 5

class PasswordResetRequestAPIView(BasePasswordResetView):
    def post(self, request, *args, **kwargs):
        """
        Şifre sıfırlama talebi alır ve doğrulama kodu gönderir.
        
        Args:
            email (str): Kullanıcının e-posta adresi
            
        Returns:
            Response: İşlem durumu ve mesaj
        """
        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "E-posta gereklidir."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Bu e-posta ile kullanıcı bulunamadı."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Rate limiting kontrolü
        try:
            email_verification = EmailVerification.objects.get(user=user)
            time_since_last_request = now() - email_verification.created_at
            if time_since_last_request < timedelta(minutes=self.RATE_LIMIT_MINUTES):
                next_allowed_time = email_verification.created_at + timedelta(minutes=self.RATE_LIMIT_MINUTES)
                return Response(
                    {
                        "error": "Çok sık kod talebi. Lütfen bekleyin.",
                        "next_request_time": next_allowed_time.isoformat(),
                        "minutes_remaining": (next_allowed_time - now()).seconds // 60
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        except EmailVerification.DoesNotExist:
            email_verification = None

        # Yeni sıfırlama kodu oluştur
        reset_code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

        # Doğrulama kaydını güncelle veya oluştur
        if email_verification:
            email_verification.verification_code = reset_code
            email_verification.created_at = now()
            email_verification.save()
        else:
            EmailVerification.objects.create(
                user=user, 
                verification_code=reset_code
            )

        # E-posta gönderimi
        try:
            send_mail(
                subject="Şifre Sıfırlama Talebi",
                message=f"""
                Merhaba {user.username},
                
                Şifre sıfırlama kodunuz: {reset_code}
                
                Bu kod {self.CODE_EXPIRY_MINUTES} dakika süreyle geçerlidir.
                Eğer bu talebi siz yapmadıysanız, lütfen dikkate almayın.
                
                İyi günler,
                VoyageView Ekibi
                """,
                from_email="noreply@voyageview.com",
                recipient_list=[email],
                fail_silently=False,
            )
        except BadHeaderError:
            return Response(
                {"error": "E-posta gönderirken geçersiz başlık bulundu."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"E-posta gönderilirken bir hata oluştu: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        expiry_time = now() + timedelta(minutes=self.CODE_EXPIRY_MINUTES)
        return Response({
            "message": "Şifre sıfırlama kodu e-posta ile gönderildi.",
            "expiry_time": expiry_time.isoformat(),
            "minutes_valid": self.CODE_EXPIRY_MINUTES
        }, status=status.HTTP_200_OK)

class PasswordResetConfirmAPIView(BasePasswordResetView):
    def check_password_history(self, user, new_password):
        """
        Yeni şifrenin son kullanılan şifrelerle aynı olmadığını kontrol eder.
        
        Args:
            user: Kullanıcı objesi
            new_password: Kontrol edilecek yeni şifre
            
        Returns:
            bool: Şifre geçmişte kullanılmışsa True, kullanılmamışsa False
        """
        # Mevcut şifre kontrolü
        if user.check_password(new_password):
            return True

        # Şifre geçmişi kontrolü
        recent_passwords = PasswordHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:self.PASSWORD_HISTORY_LIMIT]

        for password_history in recent_passwords:
            if check_password(new_password, password_history.password_hash):
                return True
                
        return False

    def update_password_history(self, user):
        """
        Kullanıcının şifre geçmişini günceller.
        
        Args:
            user: Kullanıcı objesi
        """
        # Eski şifreyi history'e kaydet
        PasswordHistory.objects.create(
            user=user,
            password_hash=user.password
        )

        # Eski kayıtları temizle
        old_passwords = PasswordHistory.objects.filter(
            user=user
        ).order_by('-created_at')[self.PASSWORD_HISTORY_LIMIT:]
        
        if old_passwords.exists():
            old_passwords.delete()

    def post(self, request, *args, **kwargs):
        """
        Şifre sıfırlama kodunu doğrular ve yeni şifreyi kaydeder.
        
        Args:
            email (str): Kullanıcının e-posta adresi
            reset_code (str): Sıfırlama kodu
            new_password (str): Yeni şifre
            
        Returns:
            Response: İşlem durumu ve mesaj
        """
        email = request.data.get("email")
        reset_code = request.data.get("reset_code")
        new_password = request.data.get("new_password")

        # Giriş doğrulaması
        if not all([email, reset_code, new_password]):
            return Response(
                {"error": "E-posta, sıfırlama kodu ve yeni şifre gereklidir."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Şifre karmaşıklık kontrolü
        try:
            validate_password_strength(new_password)
        except ValueError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            email_verification = EmailVerification.objects.get(
                user=user, 
                verification_code=reset_code
            )

            # Kod süresi kontrolü
            if now() - email_verification.created_at > timedelta(minutes=self.CODE_EXPIRY_MINUTES):
                email_verification.delete()
                return Response(
                    {
                        "error": "Sıfırlama kodunun süresi dolmuş. Lütfen yeni kod talep edin.",
                        "code_expired": True
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Önceki şifrelerle karşılaştırma
            if self.check_password_history(user, new_password):
                return Response(
                    {
                        "error": f"Bu şifre son {self.PASSWORD_HISTORY_LIMIT} şifreden biriyle aynı olamaz."
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Şifre geçmişini güncelle
            self.update_password_history(user)

            # Yeni şifreyi kaydet
            user.set_password(new_password)
            user.save()

            # Kullanılan kodu sil
            email_verification.delete()

            return Response({
                "message": "Şifre başarıyla sıfırlandı. Yeni şifrenizle giriş yapabilirsiniz.",
                "success": True
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"error": "Bu e-posta ile kullanıcı bulunamadı."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except EmailVerification.DoesNotExist:
            return Response(
                {"error": "Geçersiz veya süresi dolmuş sıfırlama kodu."}, 
                status=status.HTTP_400_BAD_REQUEST
            )