from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.crypto import get_random_string
from django.core.mail import send_mail, BadHeaderError
from backend.models import EmailVerification
from django.utils.timezone import now
from datetime import timedelta
from rest_framework.permissions import AllowAny

class ResendVerificationCodeAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Kullanıcının doğrulama kodunu tekrar gönderir.
        - Kullanıcıdan e-posta alınır.
        - Eğer doğrulama kodu süresi dolmuşsa, yeni bir kod üretilir.
        - Kod, kullanıcıya e-posta ile gönderilir.
        """
        data = request.data
        email = data.get("email")

        # E-posta kontrolü
        if not email:
            return Response({"error": "E-posta gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": f"E-posta {email} ile kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

        try:
            email_verification = EmailVerification.objects.get(user=user)

            # Doğrulama kodunun süresi dolmuşsa yeni kod oluşturuluyor
            if email_verification.created_at + timedelta(minutes=15) < now():
                email_verification.verification_code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                email_verification.created_at = now()
                email_verification.save()

            # E-posta gönderimi
            try:
                send_mail(
                    subject="E-posta Doğrulamanızı Yapın",
                    message=f"Doğrulama kodunuz: {email_verification.verification_code}.",
                    from_email="your-email@example.com",
                    recipient_list=[email],
                )
            except BadHeaderError:
                return Response({"error": "E-posta gönderirken geçersiz başlık bulundu."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": f"E-posta gönderilirken bir hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except EmailVerification.DoesNotExist:
            # Kullanıcı için yeni bir doğrulama kaydı oluşturuluyor
            verification_code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            try:
                EmailVerification.objects.create(user=user, verification_code=verification_code)
            except Exception as e:
                return Response({"error": f"Doğrulama kaydı oluşturulurken bir hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # E-posta gönderimi
            try:
                send_mail(
                    subject="E-posta Doğrulamanızı Yapın",
                    message=f"Doğrulama kodunuz: {verification_code}.",
                    from_email="your-email@example.com",
                    recipient_list=[email],
                )
            except BadHeaderError:
                return Response({"error": "E-posta gönderirken geçersiz başlık bulundu."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": f"E-posta gönderilirken bir hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Doğrulama kodu başarıyla gönderildi."}, status=status.HTTP_200_OK)
