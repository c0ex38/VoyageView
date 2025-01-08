from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.contrib.auth.hashers import check_password
from backend.models import PasswordHistory
from backend.utils import validate_password_strength

class PasswordUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    PASSWORD_HISTORY_LIMIT = 5

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
        Kullanıcı şifresini güncellemeyi sağlar.
        
        Args:
            old_password (str): Mevcut şifre
            new_password (str): Yeni şifre
            
        Returns:
            Response: İşlem durumu ve mesaj
        """
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not all([old_password, new_password]):
            return Response(
                {"error": "Eski şifre ve yeni şifre gereklidir."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        # Eski şifre kontrolü
        if not user.check_password(old_password):
            return Response(
                {"error": "Eski şifre yanlış."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Eski ve yeni şifre aynı mı kontrolü
        if old_password == new_password:
            return Response(
                {"error": "Yeni şifre eski şifre ile aynı olamaz."}, 
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

        # Önceki şifrelerle karşılaştırma
        if self.check_password_history(user, new_password):
            return Response(
                {
                    "error": f"Bu şifre son {self.PASSWORD_HISTORY_LIMIT} şifreden biriyle aynı olamaz."
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Şifre geçmişini güncelle
            self.update_password_history(user)

            # Yeni şifreyi kaydet
            user.set_password(new_password)
            user.save()

            return Response({
                "message": "Şifre başarıyla güncellendi.",
                "success": True
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Şifre güncellenirken bir hata oluştu: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )