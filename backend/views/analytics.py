from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from backend.models import Profile, Post, Comment
from django.utils.timezone import now
from datetime import timedelta

class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]  # Sadece giriş yapmış kullanıcılar erişebilir

    def get(self, request):
        """
        Kullanıcının profil etkileşimlerini gösteren analiz API'si.
        - Kullanıcının gönderdiği toplam post sayısı, yorum sayısı, beğeni sayısı gibi metrikler döndürülür.
        - Ayrıca takipçi ve takip edilen sayıları, son bir ayda yapılan yorum sayısı gibi ek bilgiler sağlanır.
        """
        user = request.user  # Giriş yapmış kullanıcıyı alıyoruz
        profile = user.profile  # Kullanıcının profil bilgilerini alıyoruz

        # Kullanıcı etkileşimleri
        total_posts = Post.objects.filter(author=user).count()  # Kullanıcının gönderdiği toplam post sayısı
        total_comments = Comment.objects.filter(author=user).count()  # Kullanıcının yazdığı toplam yorum sayısı

        # Postların toplam beğeni sayısı
        total_likes = Post.objects.filter(author=user).aggregate(Sum('likes')).get('likes__sum', 0)

        # Kullanıcı profil verileri
        followers = profile.followers.count()  # Takipçi sayısı
        following = profile.following.count()  # Takip edilen sayısı

        # Aylık etkileşim sayısı gibi ek metrikler
        # Örnek: Son bir ayda yapılan yorum sayısı
        last_month_comments = Comment.objects.filter(author=user, created_at__gte=now() - timedelta(days=30)).count()

        return Response({
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_likes": total_likes or 0,  # Beğeni sayısının 0 olduğu durumlar için kontrol ekleniyor
            "followers": followers,
            "following": following,
            "last_month_comments": last_month_comments,  # Son bir ayda yapılan yorum sayısı
        })
