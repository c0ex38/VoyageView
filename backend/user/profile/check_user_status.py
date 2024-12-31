from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

class CheckUserStatusAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Kullanıcının e-posta doğrulama durumunu kontrol eder.
        - Kullanıcı adı parametresi alınır.
        - E-posta doğrulama durumu "verified" veya "unverified" olarak döndürülür.
        - Eğer kullanıcı bulunmazsa, hata mesajı döndürülür.
        """
        username = request.query_params.get('username')

        if not username:
            return Response({"error": "Kullanıcı adı gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Kullanıcıyı veritabanında arıyoruz
            user = User.objects.get(username=username)
            if not user.profile.is_email_verified:
                # E-posta doğrulama yapılmamışsa "unverified" durumu döndürülür
                return Response({"status": "unverified"}, status=status.HTTP_200_OK)
            # E-posta doğrulandıysa "verified" durumu döndürülür
            return Response({"status": "verified"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Kullanıcı bulunamazsa hata mesajı döndürülür
            return Response({"error": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
