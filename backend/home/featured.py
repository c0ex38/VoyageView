from rest_framework.generics import ListAPIView
from backend.models import Post
from backend.serializers import PostSerializer
from django.utils.timezone import now
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Count
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

class FeaturedPostsView(ListAPIView):
    """
    Öne çıkan postları listeler.
    - Kullanıcılar kategorilerine göre filtreleyebilirler.
    - Beğeni, yorum sayısı gibi verilere göre sıralama yapılabilir.
    """
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]  # Filtreleme ve sıralama işlevselliği ekleniyor
    filterset_fields = ['category']  # Kategoriye göre filtreleme
    ordering_fields = ['total_likes', 'comment_count', 'created_at']  # Sıralama alanları
    ordering = ['-created_at']  # Varsayılan sıralama: en son oluşturulanlar

    def get_queryset(self):
        """
        Postların sorgusunu yapar.
        - Zaman dilimine göre filtreleme yapılır (hafta, ay).
        - Beğeni ve yorum sayısını anotasyon ile ekler.
        """
        time_period = self.request.query_params.get('time_period', 'week')  # Varsayılan zaman dilimi: hafta
        if time_period == 'week':
            start_date = now() - timedelta(days=7)
        elif time_period == 'month':
            start_date = now() - timedelta(days=30)
        else:
            start_date = None

        queryset = Post.objects.all()
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        # Beğeni ve yorum sayısını anotasyon ile ekliyoruz
        queryset = queryset.annotate(
            total_likes=Count('likes'),
            comment_count=Count('comments')
        )
        return queryset

class PersonalizedFeedView(generics.ListAPIView):
    """
    Kullanıcıya özel beslemeyi döndürür.
    - Kullanıcıların daha önce etkileşimde bulundukları kategorilerdeki postlar listelenir.
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]  # Sadece giriş yapmış kullanıcılar erişebilir

    def get_queryset(self):
        """
        Kullanıcı etkileşimlerine dayalı olarak, ilgili kategorilerdeki postları döndürür.
        """
        user = self.request.user
        interactions = user.userinteraction_set.values_list('post__category', flat=True).distinct()  # Kullanıcının etkileşimde bulunduğu kategoriler
        return Post.objects.filter(category__in=interactions).order_by('-created_at')  # Bu kategorilerdeki postları döndürür

class TrendingPostsView(generics.ListAPIView):
    """
    Popüler (beğenilen) postları listeler.
    - Beğeni sayısına göre sıralanır.
    """
    serializer_class = PostSerializer
    permission_classes = [AllowAny]  # Herkesin erişebileceği bir API

    def get_queryset(self):
        """
        Beğeni sayısına göre sıralanan en popüler 10 postu döndürür.
        """
        return Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:10]  # En fazla beğeniye sahip 10 postu döndürür

class MostCommentedPostsView(generics.ListAPIView):
    """
    En çok yorumlanan postları listeler.
    - Yorum sayısına göre sıralanır.
    """
    serializer_class = PostSerializer
    permission_classes = [AllowAny]  # Herkesin erişebileceği bir API

    def get_queryset(self):
        """
        Yorum sayısına göre sıralanan en çok yorumlanan 10 postu döndürür.
        """
        return Post.objects.annotate(comment_count=Count('comments')).order_by('-comment_count')[:10]  # En çok yorum alan 10 postu döndürür

class RecentPostsView(generics.ListAPIView):
    """
    En son paylaşılan postları listeler.
    - En yeni paylaşılan postlar sıralanır.
    """
    serializer_class = PostSerializer
    permission_classes = [AllowAny]  # Herkesin erişebileceği bir API

    def get_queryset(self):
        """
        En son paylaşılan 10 postu döndürür.
        """
        return Post.objects.order_by('-created_at')[:10]  # En yeni 10 postu döndürür
