from django.db.models import Count
from rest_framework import generics, permissions, status, filters
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from backend.models import Post, Notification, PostMedia, Profile, Tag, validate_video_duration
from backend.serializers import PostSerializer
from backend.permissions import IsOwner

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'description', 'location', 'tags__name']
    ordering_fields = ['likes_count', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('tags', 'media', 'comments', 'likes').annotate(
            likes_count=Count('likes')
        )

    def perform_create(self, serializer):
        # Medya dosyalarını kontrol et
        media_files = self.request.FILES.getlist('media', [])
        if not media_files:
            raise ValidationError({"media": "At least one media file is required."})

        # Video süre kontrolü
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
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

class PostLikeToggleView(generics.GenericAPIView):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        post = self.get_object()
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            message = "Like removed"
        else:
            post.likes.add(request.user)
            message = "Like added"
            # Beğeni bildirimi
            if post.author != request.user:
                Notification.objects.create(
                    user=post.author,
                    sender=request.user,
                    notification_type='like',
                    post=post
                )
        return Response({"message": message, "likes_count": post.likes.count()}, status=200)