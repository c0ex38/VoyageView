from rest_framework import generics, permissions
from backend.models import Profile, Post
from backend.serializers import PostSerializer

class FollowedUsersPostListView(generics.ListAPIView):
    """
    Takip edilen kullanıcıların postlarını listeleyen API.
    - Kullanıcı yalnızca takip ettiği kullanıcıların paylaşımlarını görebilir.
    - Postlar, en yeni olanlardan başlayarak sıralanır.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]  # Yalnızca giriş yapmış kullanıcılar erişebilir

    def get_queryset(self):
        """
        Giriş yapmış kullanıcının takip ettiği kullanıcıların postlarını alır.
        - Kullanıcının takip ettiği kişilerin tüm postlarını filtreler ve sıralar.
        """
        user = self.request.user  # Giriş yapmış kullanıcıyı alıyoruz
        # Kullanıcının takip ettiği kullanıcıların listesine erişiyoruz
        followed_users = user.profile.following.all().values_list('user', flat=True)
        # Takip edilen kullanıcıların postlarını sıralı bir şekilde döndürüyoruz
        return Post.objects.filter(author__in=followed_users).order_by('-created_at')
