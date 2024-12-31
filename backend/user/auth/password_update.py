from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

class PasswordUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Kullanıcı şifresini güncellemeyi sağlar.
        - Kullanıcıdan eski şifre ve yeni şifre alınır.
        - Eski şifre doğruysa yeni şifre belirlenir.
        - Eğer eski şifre yanlışsa, hata mesajı döndürülür.
        """
        old_password = request.data.get("old_password")  # Eski şifreyi alıyoruz
        new_password = request.data.get("new_password")  # Yeni şifreyi alıyoruz

        if not old_password or not new_password:
            # Eğer eski şifre veya yeni şifre verilmemişse, hata döndür
            return Response({"error": "Eski şifre ve yeni şifre gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user  # Giriş yapmış kullanıcıyı alıyoruz

        # Eski şifrenin doğru olup olmadığını kontrol ediyoruz
        if not user.check_password(old_password):
            # Eğer eski şifre yanlışsa, hata mesajı döndür
            return Response({"error": "Eski şifre yanlış."}, status=status.HTTP_400_BAD_REQUEST)

        # Yeni şifreyi ayarlıyoruz
        user.set_password(new_password)
        user.save()  # Kullanıcıyı güncelliyoruz

        return Response({"message": "Şifre başarıyla güncellendi."}, status=status.HTTP_200_OK)
