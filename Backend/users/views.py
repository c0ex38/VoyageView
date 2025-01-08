from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
import random

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle
from rest_framework.parsers import MultiPartParser

from .models import CustomUser, VerificationCode
from .serializers import (
    RegisterSerializer, 
    ProfileUpdateSerializer, 
    UserProfileSerializer, 
    UserSettingsSerializer
)
from blog.models import BlogPost, Comment

User = get_user_model()

def send_verification_email(email, code):
    send_mail(
        'E-posta Doğrulama Kodu',
        f'Doğrulama kodunuz: {code}',
        'noreply@voyageview.com',
        [email],
        fail_silently=False,
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                password = serializer.validated_data.get('password')
                try:
                    validate_password(password)
                except ValidationError as e:
                    return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

                user = serializer.save()
                
                verification = VerificationCode.create_verification_code(
                    user=user,
                    purpose='EMAIL',
                    expiry_minutes=1440  # 24 saat
                )

                send_mail(
                    'VoyageView\'e Hoş Geldiniz!',
                    f'''Merhaba {user.username},

VoyageView ailesine hoş geldiniz! Hesabınızı doğrulamak için kodunuz: {verification.code}

Bu kod 24 saat geçerlidir.

Saygılarımızla,
VoyageView Ekibi''',
                    'noreply@voyageview.com',
                    [user.email],
                    fail_silently=False,
                )

                return Response({
                    'message': 'Kayıt başarılı! Lütfen e-postanızı kontrol edin.',
                    'user_id': user.id,
                    'email': user.email,
                    'expires_at': verification.expires_at
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('code')
        user_id = request.data.get('user_id')
        
        try:
            verification = VerificationCode.objects.filter(
                user_id=user_id,
                purpose='EMAIL',
                code=code,
                is_used=False,
                expires_at__gt=timezone.now()
            ).latest('created_at')
            
            if verification.is_valid():
                user = verification.user
                user.is_active = True
                user.is_email_verified = True
                user.save()
                
                verification.use()
                
                return Response({
                    'message': 'Email başarıyla doğrulandı'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Geçersiz veya süresi dolmuş doğrulama kodu'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except VerificationCode.DoesNotExist:
            return Response({
                'error': 'Geçersiz doğrulama kodu'
            }, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id, is_active=False)
            
            # Yeni doğrulama kodu oluştur
            verification = VerificationCode.create_verification_code(
                user=user,
                purpose='EMAIL'
            )
            
            # Email gönderme işlemi
            send_verification_email(user.email, verification.code)
            
            return Response({
                'message': 'Doğrulama kodu tekrar gönderildi'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'Kullanıcı bulunamadı'
            }, status=status.HTTP_404_NOT_FOUND)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            
            # 6 haneli rastgele kod oluştur
            reset_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Kodu kullanıcı modeline kaydet (ya da cache/redis kullan)
            user.password_reset_code = reset_code
            user.save()
            
            # Email gönder
            send_mail(
                'Şifre Sıfırlama Kodu',
                f'''Merhaba {user.username},

Şifre sıfırlama kodunuz: {reset_code}

Bu kodu kimseyle paylaşmayın.
Eğer bu isteği siz yapmadıysanız, bu emaili görmezden gelebilirsiniz.

Saygılarımızla,
VoyageView Ekibi''',
                'noreply@voyageview.com',
                [user.email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Şifre sıfırlama kodu email adresinize gönderildi.'
            })
            
        except User.DoesNotExist:
            # Güvenlik için kullanıcı bulunamasa bile aynı mesajı dön
            return Response({
                'message': 'Şifre sıfırlama kodu email adresinize gönderildi.'
            })
        except Exception as e:
            return Response({
                'message': 'Bir hata oluştu. Lütfen daha sonra tekrar deneyin.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        reset_code = request.data.get('reset_code')
        new_password = request.data.get('password')
        
        try:
            user = User.objects.get(email=email)
            
            # Kod kontrolü
            if not hasattr(user, 'password_reset_code') or user.password_reset_code != reset_code:
                return Response({
                    'message': 'Geçersiz veya süresi dolmuş kod.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Şifreyi güncelle
            user.set_password(new_password)
            user.password_reset_code = None  # Kodu sıfırla
            user.save()
            
            # Başarılı email gönder
            send_mail(
                'Şifreniz Değiştirildi',
                f'''Merhaba {user.username},

Şifreniz başarıyla değiştirildi.
Eğer bu işlemi siz yapmadıysanız, hemen bizimle iletişime geçin.

Saygılarımızla,
VoyageView Ekibi''',
                'noreply@voyageview.com',
                [user.email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Şifreniz başarıyla değiştirildi.'
            })
            
        except User.DoesNotExist:
            return Response({
                'message': 'Geçersiz email adresi.'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': 'Bir hata oluştu. Lütfen daha sonra tekrar deneyin.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get(self, request):
        serializer = ProfileUpdateSerializer(request.user)
        user_stats = {
            "followers_count": request.user.followers.count(),
            "following_count": request.user.following.count(),
            "total_posts": BlogPost.objects.filter(author=request.user).count(),
            "total_likes": BlogPost.objects.filter(author=request.user).aggregate(
                total_likes=models.Sum('like_count')
            )['total_likes'] or 0
        }
        
        response_data = {
            "profile": serializer.data,
            "stats": user_stats,
            "recent_activity": self.get_recent_activity(request.user)
        }
        return Response(response_data)

    def get_recent_activity(self, user):
        recent_posts = BlogPost.objects.filter(author=user).order_by('-created_at')[:5]
        recent_comments = Comment.objects.filter(user=user).order_by('-created_at')[:5]
        
        return {
            "recent_posts": [{
                "id": post.id,
                "title": post.title,
                "created_at": post.created_at,
                "likes": post.like_count
            } for post in recent_posts],
            "recent_comments": [{
                "id": comment.id,
                "post_title": comment.blog_post.title,
                "created_at": comment.created_at
            } for comment in recent_comments]
        }

    def put(self, request):
        serializer = ProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            if 'profile_photo' in request.FILES:
                photo = request.FILES['profile_photo']
                if photo.size > 5 * 1024 * 1024:  # 5MB limit
                    return Response({
                        'error': 'Profil fotoğrafı 5MB\'dan büyük olamaz'
                    }, status=status.HTTP_400_BAD_REQUEST)

            updated_user = serializer.save()
            
            changes = {
                field: value for field, value in serializer.validated_data.items()
            }
            
            response_data = {
                "message": "Profil başarıyla güncellendi",
                "changes": changes,
                "profile": ProfileUpdateSerializer(updated_user).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        """
        Bir kullanıcıyı takip et veya takibi bırak.
        - Takip edilen kullanıcıya bildirim gönderir (isteğe bağlı).
        - Takipçi ve takip edilen sayısını döndürür.
        """
        user_to_follow = get_object_or_404(CustomUser, id=user_id)

        if request.user == user_to_follow:
            return Response({"error": "You cannot follow yourself."}, status=400)

        if request.user in user_to_follow.followers.all():
            user_to_follow.followers.remove(request.user)
            action = "unfollowed"
        else:
            user_to_follow.followers.add(request.user)
            action = "followed"
        return Response(
            {
                "message": f"You have {action} {user_to_follow.username}.",
            },
            status=200,
        )


class UserStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        time_period = request.query_params.get('period', 'all')  # all, month, week

        # Zaman filtresini ayarla
        if time_period == 'month':
            time_filter = timezone.now() - timezone.timedelta(days=30)
        elif time_period == 'week':
            time_filter = timezone.now() - timezone.timedelta(days=7)
        else:
            time_filter = None

        # Blog istatistikleri
        blog_query = BlogPost.objects.filter(author=user)
        if time_filter:
            blog_query = blog_query.filter(created_at__gte=time_filter)

        blog_stats = blog_query.aggregate(
            total_posts=models.Count('id'),
            total_likes=models.Sum('like_count'),
            total_views=models.Sum('view_count'),
            avg_likes_per_post=models.Avg('like_count')
        )

        # Kategori bazlı analiz
        category_stats = blog_query.values('category__name').annotate(
            post_count=models.Count('id'),
            total_likes=models.Sum('like_count')
        )

        # En popüler yazılar
        top_posts = blog_query.order_by('-like_count')[:5].values(
            'id', 'title', 'like_count', 'view_count', 'created_at'
        )

        stats = {
            "time_period": time_period,
            "blog_statistics": {
                "total_posts": blog_stats['total_posts'] or 0,
                "total_likes": blog_stats['total_likes'] or 0,
                "total_views": blog_stats['total_views'] or 0,
                "avg_likes_per_post": round(blog_stats['avg_likes_per_post'] or 0, 2)
            },
            "category_analysis": list(category_stats),
            "top_performing_posts": list(top_posts),
            "engagement_rate": self.calculate_engagement_rate(blog_stats)
        }
        return Response(stats, status=200)

    def calculate_engagement_rate(self, stats):
        if not stats['total_posts'] or not stats['total_views']:
            return 0
        return round((stats['total_likes'] or 0) / stats['total_views'] * 100, 2)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({
                    'message': 'Başarıyla çıkış yapıldı'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Refresh token gerekli'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Çıkış yapılırken bir hata oluştu'
            }, status=status.HTTP_400_BAD_REQUEST)


class CheckFieldAvailabilityView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        field = request.data.get('field')
        value = request.data.get('value')
        
        if not field or not value:
            return Response({
                'error': 'Field ve value parametreleri gerekli'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if field not in ['username', 'email']:
            return Response({
                'error': 'Geçersiz field parametresi'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Field'a göre sorgu yap
        exists = User.objects.filter(**{field: value}).exists()
        
        return Response({
            'available': not exists,
            'message': f"Bu {field} {'kullanılabilir' if not exists else 'kullanılamaz'}"
        })

@api_view(['POST'])
def reset_password_request(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        
        # 6 haneli rastgele kod oluştur
        reset_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Kodu kullanıcı modeline kaydet (ya da cache/redis kullan)
        user.password_reset_code = reset_code
        user.save()
        
        # Email gönder
        send_mail(
            'Şifre Sıfırlama Kodu',
            f'''Merhaba {user.username},

Şifre sıfırlama kodunuz: {reset_code}

Bu kodu kimseyle paylaşmayın.
Eğer bu isteği siz yapmadıysanız, bu emaili görmezden gelebilirsiniz.

Saygılarımızla,
VoyageView Ekibi''',
            'noreply@voyageview.com',
            [user.email],
            fail_silently=False,
        )
        
        return Response({
            'message': 'Şifre sıfırlama kodu email adresinize gönderildi.'
        })
        
    except User.DoesNotExist:
        # Güvenlik için kullanıcı bulunamasa bile aynı mesajı dön
        return Response({
            'message': 'Şifre sıfırlama kodu email adresinize gönderildi.'
        })
    except Exception as e:
        return Response({
            'message': 'Bir hata oluştu. Lütfen daha sonra tekrar deneyin.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def reset_password_confirm(request):
    email = request.data.get('email')
    reset_code = request.data.get('reset_code')
    new_password = request.data.get('password')
    
    try:
        user = User.objects.get(email=email)
        
        # Kod kontrolü
        if not hasattr(user, 'password_reset_code') or user.password_reset_code != reset_code:
            return Response({
                'message': 'Geçersiz veya süresi dolmuş kod.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Şifreyi güncelle
        user.set_password(new_password)
        user.password_reset_code = None  # Kodu sıfırla
        user.save()
        
        # Başarılı email gönder
        send_mail(
            'Şifreniz Değiştirildi',
            f'''Merhaba {user.username},

Şifreniz başarıyla değiştirildi.
Eğer bu işlemi siz yapmadıysanız, hemen bizimle iletişime geçin.

Saygılarımızla,
VoyageView Ekibi''',
            'noreply@voyageview.com',
            [user.email],
            fail_silently=False,
        )
        
        return Response({
            'message': 'Şifreniz başarıyla değiştirildi.'
        })
        
    except User.DoesNotExist:
        return Response({
            'message': 'Geçersiz email adresi.'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'message': 'Bir hata oluştu. Lütfen daha sonra tekrar deneyin.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username=None):
        if username:
            user = get_object_or_404(User, username=username)
        else:
            user = request.user

        serializer = UserProfileSerializer(user, context={'request': request})
        
        # Blog istatistiklerini hesapla
        blog_stats = BlogPost.objects.filter(author=user).aggregate(
            total_posts=models.Count('id'),  # Şimdi models.Count kullanabiliriz
            total_likes=models.Sum('like_count'),  # Ve models.Sum da kullanabiliriz
            total_reads=models.Sum('read_count')
        )

        return Response({
            'profile': serializer.data,
            'blog_stats': blog_stats
        })

    def put(self, request, username=None):
        # Sadece 'me' veya kendi kullanıcı adıyla güncelleme yapılabilir
        if not username or username == 'me' or username == request.user.username:
            user = request.user
        else:
            return Response(
                {'error': 'Başka bir kullanıcının profilini güncelleyemezsiniz'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserSettingsSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            # Güncellemeden sonra tam profil bilgilerini dön
            profile_serializer = UserProfileSerializer(user, context={'request': request})
            return Response({
                'message': 'Profil başarıyla güncellendi',
                'profile': profile_serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
