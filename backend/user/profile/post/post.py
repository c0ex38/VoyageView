from django.db.models import Count
from rest_framework import generics, permissions, status, filters
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from backend.models import Post, Notification, PostMedia, Profile, Tag, validate_video_duration
from backend.serializers import PostSerializer
from backend.permissions import IsOwner

class PostListCreateView(generics.ListCreateAPIView):
    """
    Postları listeleyen ve yeni post oluşturan API.
    - Kullanıcılar, kategoriye göre filtreleme yapabilir, başlık, açıklama, konum ve etiketlere göre arama yapabilir.
    - Postlar, beğeni sayısına veya oluşturulma tarihine göre sıralanabilir.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Yalnızca giriş yapmış kullanıcılar post oluşturabilir
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]  # Filtreleme ve sıralama
    filterset_fields = ['category']  # Kategoriye göre filtreleme
    search_fields = ['title', 'description', 'location', 'tags__name']  # Arama alanları
    ordering_fields = ['likes_count', 'created_at']  # Sıralama alanları
    ordering = ['-created_at']  # Varsayılan sıralama (en yeni postlar en üstte)

    def get_queryset(self):
        """
        Postları getiren ve ilişkili alanları (tags, media, comments, likes) ekleyen sorgu.
        """
        queryset = super().get_queryset()
        return queryset.prefetch_related('tags', 'media', 'comments', 'likes').annotate(
            likes_count=Count('likes')  # Beğeni sayısı ekleniyor
        )

    def perform_create(self, serializer):
        """
        Yeni bir post oluşturulmadan önce medya dosyalarını kontrol eder.
        - En az bir medya dosyası gerekli.
        - Video süresi kontrol edilir.
        """
        media_files = self.request.FILES.getlist('media', [])
        if not media_files:
            raise ValidationError({"media": "En az bir medya dosyası gereklidir."})

        # Video süresi kontrolü
        for media_file in media_files:
            if media_file.content_type.startswith('video'):
                try:
                    validate_video_duration(media_file)
                except ValueError as e:
                    raise ValidationError({"media": str(e)})

        # Post'u kaydet
        post = serializer.save()

        # Takipçilere bildirim gönder
        if post.author.profile:
            followers = Profile.objects.filter(following=post.author.profile)
            for follower in followers:
                Notification.objects.create(
                    user=follower.user,
                    sender=post.author,
                    notification_type='post',
                    post=post
                )


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Mevcut bir postu görüntüleme, güncelleme veya silme işlemi yapan API.
    - Kullanıcı yalnızca kendi postlarını güncelleyebilir.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        """
        Kullanıcı sadece kendi postunu güncelleyebilir.
        """
        serializer.save(author=self.request.user)


class PostLikeToggleView(generics.GenericAPIView):
    """
    Bir postu beğenme veya beğeniyi kaldırma işlemi yapan API.
    - Kullanıcı bir postu beğendiğinde, post sahibine bildirim gönderilir.
    """
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        post = self.get_object()
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            message = "Beğeni kaldırıldı"
        else:
            post.likes.add(request.user)
            message = "Beğeni eklendi"
            # Beğeni bildirimi
            if post.author != request.user:
                Notification.objects.create(
                    user=post.author,  # Post sahibine bildirim
                    sender=request.user,  # Beğeniyi yapan kullanıcı
                    notification_type='like',
                    post=post
                )
        return Response({"message": message, "likes_count": post.likes.count()}, status=200)
