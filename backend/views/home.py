from rest_framework import generics
from django.db.models import Count
from backend.models import Post
from backend.serializers import PostSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated

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
