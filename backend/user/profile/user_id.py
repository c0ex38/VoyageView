from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny

class GetUserIdAPIView(APIView):
    """
    Kullanıcı adı ile kullanıcı ID'sini sorgular.
    - Kullanıcı adı parametresi ile kullanıcı ID'sini döndürür.
    - Eğer kullanıcı bulunamazsa hata mesajı döner.
    """
    permission_classes = [AllowAny]  # Herkesin erişebileceği bir API

    def get(self, request):
        """
        Kullanıcı adı ile kullanıcı ID'sini döndürür.
        - Kullanıcı adı alınır.
        - Kullanıcı bulunamazsa hata mesajı döndürülür.
        """
        username = request.query_params.get('username')  # Kullanıcı adı parametresini alıyoruz
        if not username:
            return Response({"error": "Kullanıcı adı gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Kullanıcıyı veritabanında arıyoruz
            user = User.objects.get(username=username)
            return Response({"user_id": user.id}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Kullanıcı bulunamazsa hata mesajı döndürüyoruz
            return Response({"error": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
