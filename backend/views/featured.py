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
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category']  # Kategoriye göre filtreleme
    ordering_fields = ['total_likes', 'comment_count', 'created_at']  # Sıralama alanları
    ordering = ['-created_at']  # Varsayılan sıralama

    def get_queryset(self):
        time_period = self.request.query_params.get('time_period', 'week')
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



# Personalized Feed View
class PersonalizedFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        interactions = user.userinteraction_set.values_list('post__category', flat=True).distinct()
        return Post.objects.filter(category__in=interactions).order_by('-created_at')

# Trending Posts View
class TrendingPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:10]

# Most Commented Posts View
class MostCommentedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Post.objects.annotate(comment_count=Count('comments')).order_by('-comment_count')[:10]

# Recent Posts View
class RecentPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Post.objects.order_by('-created_at')[:10]
