from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from backend.models import Profile
from backend.serializers import ProfileSerializer

class ProfileDetailView(APIView):
    """
    Kullanıcı profilini görüntüleme ve güncelleme işlevsini sağlar.
    - Kullanıcı giriş yaptıysa, profil bilgileri görüntülenebilir ve güncellenebilir.
    - Güncelleme işlemi sadece POST isteği ile yapılabilir.
    """
    permission_classes = [IsAuthenticated]  # Sadece giriş yapmış kullanıcılar erişebilir

    def get(self, request):
        """
        Giriş yapmış kullanıcının profilini döner.
        """
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        """
        Giriş yapmış kullanıcının profil bilgilerini günceller.
        - Yeni profil bilgileri POST isteği ile alınır.
        """
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # Profil bilgilerini günceller
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
