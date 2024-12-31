from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.crypto import get_random_string
from backend.models import EmailVerification
from django.core.mail import EmailMultiAlternatives
from rest_framework.permissions import AllowAny
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

class RegisterUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Yeni kullanıcı kaydı oluşturur.
        - Kullanıcı adı, şifre ve e-posta bilgileri alınır.
        - Şifre güvenliği kontrol edilir.
        - Kullanıcı kaydedilir ve doğrulama kodu e-posta ile gönderilir.
        """
        data = request.data

        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

        # Kullanıcı adı, şifre ve e-posta boşsa hata döndürülür
        if not username or not password or not email:
            return Response({"error": "Kullanıcı adı, şifre ve e-posta gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        # Kullanıcı adı ve e-posta zaten mevcutsa hata döndürülür
        if User.objects.filter(username=username).exists():
            return Response({"error": "Kullanıcı adı zaten mevcut."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "E-posta zaten mevcut."}, status=status.HTTP_400_BAD_REQUEST)

        # Şifre güvenliği kontrolü yapılır
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({"error": f"Şifre hatası: {e.messages}"}, status=status.HTTP_400_BAD_REQUEST)

        # Yeni kullanıcı oluşturulur
        user = User.objects.create_user(username=username, password=password, email=email)

        # Doğrulama kodu üretilir
        verification_code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

        try:
            # Doğrulama kodu veritabanına kaydedilir
            EmailVerification.objects.create(user=user, verification_code=verification_code)

            # E-posta ile doğrulama kodu gönderilir
            subject = "VoyageView - E-posta Doğrulamanızı Yapın"
            text_content = f"Merhaba {username},\n\nVoyageView'a kaydolduğunuz için teşekkür ederiz! Lütfen aşağıdaki doğrulama kodunu kullanarak e-posta adresinizi doğrulayın:\n\nDoğrulama Kodu: {verification_code}\n\nEğer kayıt yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.\n\nSaygılarımızla,\nVoyageView Ekibi"

            html_content = f"""
            <html>
            <body>
                <div class="container">
                    <div class="logo">
                        <img src="https://example.com/logo.png" alt="VoyageView Logo" class="h-16">
                    </div>
                    <div class="content">
                        <p>VoyageView'a hoş geldiniz, {username}!</p>
                        <p>VoyageView'a katıldığınız için teşekkür ederiz! Kaydınızı tamamlamak için lütfen e-posta adresinizi doğrulayın.</p>
                        <div class="verification-code">
                            {verification_code}
                        </div>
                        <p>Eğer kayıt yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.</p>
                        <p>Aramıza katıldığınız için heyecanlıyız!</p>
                        <p>Saygılarla,<br>
                        <strong>VoyageView Ekibi</strong></p>
                    </div>
                    <div class="footer">
                        Herhangi bir sorunuz varsa, bizimle iletişime geçin: <a href="mailto:support@voyageview.com">support@voyageview.com</a>
                    </div>
                </div>
            </body>
            </html>
            """

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email="support@voyageview.com",
                to=[email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

        except Exception as e:
            # Hata durumunda kullanıcıyı sil
            user.delete()
            return Response({"error": f"Bir hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "Kullanıcı başarıyla kaydedildi. Lütfen e-posta adresinizi doğrulayın.",
            "user_id": user.id,
        }, status=status.HTTP_201_CREATED)
