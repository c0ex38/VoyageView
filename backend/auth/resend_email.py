from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.crypto import get_random_string
from django.core.mail import send_mail, BadHeaderError
from backend.models import EmailVerification, Profile
from django.utils.timezone import now
from datetime import timedelta
from rest_framework.permissions import AllowAny

class ResendVerificationCodeAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Kullanıcının doğrulama kodunu tekrar gönderir.
        - Kullanıcıdan e-posta alınır.
        - E-posta doğrulama durumu kontrol edilir.
        - Eğer doğrulama kodu süresi dolmuşsa, yeni bir kod üretilir.
        - Kod, kullanıcıya e-posta ile gönderilir.
        """
        data = request.data
        email = data.get("email")

        # E-posta kontrolü
        if not email:
            return Response(
                {"error": "E-posta gereklidir."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            profile = Profile.objects.get(user=user)

            # E-posta zaten doğrulanmış mı kontrolü
            if profile.is_email_verified:
                return Response(
                    {"error": "Bu e-posta adresi zaten doğrulanmış."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except User.DoesNotExist:
            return Response(
                {"error": f"E-posta {email} ile kullanıcı bulunamadı."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Profile.DoesNotExist:
            return Response(
                {"error": "Kullanıcı profili bulunamadı."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            email_verification = EmailVerification.objects.get(user=user)

            # Son 5 dakika içinde kod gönderilmiş mi kontrolü
            if now() - email_verification.created_at < timedelta(minutes=5):
                return Response(
                    {
                        "error": "Çok sık kod talebi. Lütfen 5 dakika bekleyin.",
                        "next_request_time": (email_verification.created_at + timedelta(minutes=5)).isoformat()
                    }, 
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Doğrulama kodunun süresi dolmuşsa yeni kod oluştur
            if email_verification.created_at + timedelta(minutes=15) < now():
                email_verification.verification_code = get_random_string(
                    length=6, 
                    allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                )
                email_verification.created_at = now()
                email_verification.save()

        except EmailVerification.DoesNotExist:
            # Yeni doğrulama kaydı oluştur
            verification_code = get_random_string(
                length=6, 
                allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            )
            try:
                email_verification = EmailVerification.objects.create(
                    user=user, 
                    verification_code=verification_code
                )
            except Exception as e:
                return Response(
                    {"error": f"Doğrulama kaydı oluşturulurken bir hata oluştu: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # E-posta gönderimi
        try:
            send_mail(
                subject="E-posta Doğrulamanızı Yapın",
                message=f"""
                Merhaba {user.username},
                
                E-posta adresinizi doğrulamak için kodunuz: {email_verification.verification_code}
                
                Bu kod 15 dakika süreyle geçerlidir.
                
                İyi günler,
                VoyageView Ekibi
                """,
                from_email="your-email@example.com",
                recipient_list=[email],
            )
        except BadHeaderError:
            return Response(
                {"error": "E-posta gönderirken geçersiz başlık bulundu."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"E-posta gönderilirken bir hata oluştu: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            "message": "Doğrulama kodu başarıyla gönderildi.",
            "expiry_time": (email_verification.created_at + timedelta(minutes=15)).isoformat()
        }, status=status.HTTP_200_OK)