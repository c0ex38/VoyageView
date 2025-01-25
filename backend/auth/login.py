from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.utils.timezone import now
from backend.models import Profile

class LoginUserAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    MAX_LOGIN_ATTEMPTS = 5  # Maksimum giriş denemesi
    BLOCK_TIME = 90  # Engelleme süresi (saniye)
    ATTEMPT_RESET_TIME = 24 * 60 * 60  # Deneme sayısı sıfırlama süresi (24 saat)

    def get_client_ip(self, request):
        """
        İstemci IP adresini alır.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def get_login_attempts(self, username, ip):
        """
        Kullanıcı adı ve IP için giriş denemelerini alır.
        """
        username_attempts = cache.get(f'login_attempts_{username}', 0)
        ip_attempts = cache.get(f'login_attempts_ip_{ip}', 0)
        return username_attempts, ip_attempts

    def increment_login_attempts(self, username, ip):
        """
        Başarısız giriş denemelerini artırır.
        """
        username_attempts, ip_attempts = self.get_login_attempts(username, ip)
        
        cache.set(
            f'login_attempts_{username}', 
            username_attempts + 1, 
            timeout=self.ATTEMPT_RESET_TIME
        )
        cache.set(
            f'login_attempts_ip_{ip}', 
            ip_attempts + 1, 
            timeout=self.ATTEMPT_RESET_TIME
        )

        return username_attempts + 1, ip_attempts + 1

    def check_login_blocked(self, username, ip):
        """
        Giriş engelini kontrol eder.
        """
        username_attempts, ip_attempts = self.get_login_attempts(username, ip)
        
        if username_attempts >= self.MAX_LOGIN_ATTEMPTS:
            block_time = cache.ttl(f'login_attempts_{username}')
            return True, {
                "error": "Çok fazla başarısız deneme. Hesap geçici olarak kilitlendi.",
                "remaining_time": block_time,
                "blocked_until": (now() + timedelta(seconds=block_time)).isoformat()
            }
            
        if ip_attempts >= self.MAX_LOGIN_ATTEMPTS * 2:  # IP için daha yüksek limit
            block_time = cache.ttl(f'login_attempts_ip_{ip}')
            return True, {
                "error": "Bu IP adresinden çok fazla başarısız deneme yapıldı.",
                "remaining_time": block_time,
                "blocked_until": (now() + timedelta(seconds=block_time)).isoformat()
            }
            
        return False, None

    def post(self, request, *args, **kwargs):
        """
        Kullanıcı girişi API endpoint'i.
        
        - Kullanıcı adı ve şifre doğrulaması
        - Başarısız giriş denemesi takibi
        - IP bazlı koruma
        - Hesap durumu kontrolü
        - JWT token üretimi
        """
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Kullanıcı adı ve şifre gereklidir."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        client_ip = self.get_client_ip(request)
        
        # Giriş engeli kontrolü
        is_blocked, block_info = self.check_login_blocked(username, client_ip)
        if is_blocked:
            return Response(block_info, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Kullanıcı doğrulama
        user = authenticate(username=username, password=password)

        if user:
            if not user.is_active:
                return Response(
                    {"error": "Hesabınız pasif durumda. Lütfen destek ile iletişime geçin."}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            try:
                profile = Profile.objects.get(user=user)
                if not profile.is_email_verified:
                    return Response(
                        {"error": "E-posta adresiniz henüz doğrulanmamış."}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Profile.DoesNotExist:
                return Response(
                    {"error": "Kullanıcı profili bulunamadı."}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Başarılı giriş - token üretimi
            refresh = RefreshToken.for_user(user)
            
            # Giriş denemelerini sıfırla
            cache.delete(f'login_attempts_{username}')
            cache.delete(f'login_attempts_ip_{client_ip}')

            return Response({
                "message": "Giriş başarılı",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_staff": user.is_staff
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
            }, status=status.HTTP_200_OK)

        else:
            # Başarısız giriş - deneme sayısını artır
            username_attempts, ip_attempts = self.increment_login_attempts(username, client_ip)
            
            remaining_attempts = self.MAX_LOGIN_ATTEMPTS - username_attempts
            
            return Response({
                "error": "Geçersiz kullanıcı adı veya şifre.",
                "remaining_attempts": max(remaining_attempts, 0),
                "warning": "Kalan deneme hakkınız: {}".format(max(remaining_attempts, 0))
            }, status=status.HTTP_400_BAD_REQUEST)