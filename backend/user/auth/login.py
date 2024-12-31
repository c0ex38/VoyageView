from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache

MAX_LOGIN_ATTEMPTS = 5
BLOCK_TIME = 90

class LoginUserAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Kullanıcı girişi, kimlik doğrulama ve giriş denemesi sınırlaması işlevlerini gerçekleştirir.
        - Kullanıcı adı ve şifre doğrulaması yapılır.
        - Başarısız giriş denemeleri takip edilir ve belirtilen sınır aşılırsa geçici olarak engellenir.
        - Kimlik doğrulama başarılı olursa, JWT token'ları (refresh ve access) oluşturulur.
        - Kimlik doğrulama başarısız olursa, giriş denemeleri sayısı arttırılır ve hata mesajı döndürülür.
        """
        data = request.data
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return Response({"error": "Kullanıcı adı ve şifre gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        login_attempts = cache.get(f'login_attempts_{username}', 0)

        if login_attempts >= MAX_LOGIN_ATTEMPTS:
            return Response(
                {"error": "Çok fazla giriş denemesi yaptınız. Lütfen daha sonra tekrar deneyin."},
                status=status.HTTP_403_FORBIDDEN
            )

        user = authenticate(username=username, password=password)

        if user:
            if not user.is_active:
                return Response({"error": "Hesabınız pasif durumda. Lütfen destek ile iletişime geçin."}, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)

            cache.set(f'login_attempts_{username}', 0, timeout=BLOCK_TIME)

            return Response({
                "message": "Giriş başarılı",
                "user": {"username": user.username, "email": user.email},
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        else:
            cache.set(f'login_attempts_{username}', login_attempts + 1, timeout=BLOCK_TIME)
            return Response({"error": "Geçersiz kullanıcı adı veya şifre."}, status=status.HTTP_400_BAD_REQUEST)
