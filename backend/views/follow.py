from rest_framework import generics, permissions
from backend.models import Profile, Post
from backend.serializers import PostSerializer

class FollowedUsersPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]  # Yetkilendirme zorunlu

    def get_queryset(self):
        user = self.request.user
        # Takip edilen kullanıcıların postlarını filtrele
        followed_users = user.profile.following.all().values_list('user', flat=True)
        return Post.objects.filter(author__in=followed_users).order_by('-created_at')