# views/auth/logout.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache

class LogoutUserAPIView(APIView):
   permission_classes = [IsAuthenticated]

   def post(self, request, *args, **kwargs):
       """
       Kullanıcı çıkış işlemini gerçekleştirir.
       - JWT token'ı blacklist'e eklenir
       - Önbellekteki oturum verileri temizlenir
       
       Returns:
           Response: İşlem durumu ve mesaj
       """
       try:
           # Refresh token'ı al
           refresh_token = request.data.get("refresh_token")
           
           if not refresh_token:
               return Response(
                   {"error": "Refresh token gereklidir."}, 
                   status=status.HTTP_400_BAD_REQUEST
               )

           # Token'ı blacklist'e ekle
           token = RefreshToken(refresh_token)
           token.blacklist()

           # Kullanıcıya ait önbellekteki verileri temizle
           cache.delete_many([
               f'login_attempts_{request.user.username}',
               f'login_attempts_ip_{request.META.get("REMOTE_ADDR")}',
               f'user_session_{request.user.id}'
           ])

           return Response(
               {
                   "message": "Başarıyla çıkış yapıldı.",
                   "success": True
               },
               status=status.HTTP_200_OK
           )

       except Exception as e:
           return Response(
               {
                   "error": "Çıkış yapılırken bir hata oluştu.",
                   "detail": str(e)
               }, 
               status=status.HTTP_400_BAD_REQUEST
           )