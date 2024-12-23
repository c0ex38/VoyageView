from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.crypto import get_random_string
from backend.models import EmailVerification
from django.core.mail import EmailMultiAlternatives
from rest_framework.permissions import AllowAny

class RegisterUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data

        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

        if not username or not password or not email:
            return Response({"error": "Username, password, and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Kullanıcı oluşturma
        user = User.objects.create_user(username=username, password=password, email=email)

        # Doğrulama kodu üretimi
        verification_code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

        try:
            # Veritabanında sakla
            EmailVerification.objects.create(user=user, verification_code=verification_code)

            # E-posta gönderimi
            subject = "Welcome to VoyageView - Verify Your Email"
            text_content = f"Dear {username},\n\nThank you for registering at VoyageView! Please verify your email address using the code below:\n\nVerification Code: {verification_code}\n\nIf you didn't sign up, you can safely ignore this email.\n\nBest regards,\nVoyageView Team"

            html_content = f"""
            <html>
            <body>
                <div class="container">
                    <div class="logo">
                        <img src="https://example.com/logo.png" alt="VoyageView Logo" class="h-16">
                    </div>
                    <div class="content">
                        <p>Welcome to VoyageView, {username}!</p>
                        <p>Thank you for joining VoyageView! Please verify your email address to complete your registration.</p>
                        <div class="verification-code">
                            {verification_code}
                        </div>
                        <p>If you didn't sign up, you can safely ignore this email.</p>
                        <p>We're excited to have you on board!</p>
                        <p>Best regards,<br>
                        <strong>VoyageView Team</strong></p>
                    </div>
                    <div class="footer">
                        If you have any questions, contact us at <a href="mailto:support@voyageview.com">support@voyageview.com</a>
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
            user.delete()  # Hata durumunda kullanıcıyı sil
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "User registered successfully. Please verify your email.",
            "user_id": user.id,
        }, status=status.HTTP_201_CREATED)
