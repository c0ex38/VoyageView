from rest_framework import generics, permissions, status
from rest_framework.response import Response
from backend.models import Follow
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.models import Profile, Post
from backend.serializers import ProfileSerializer
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
        # Kullanıcının takip ettiği kullanıcıları alıyoruz (Follow modelini kullanarak)
        followed_users = Follow.objects.filter(user=user).values_list('followed_user', flat=True)
        # Takip edilen kullanıcıların postlarını sıralı bir şekilde döndürüyoruz
        return Post.objects.filter(author__in=followed_users).order_by('-created_at')


class FollowToggleView(generics.GenericAPIView):
    """
    Kullanıcı birisini takip etmeye başlar veya takibi bırakır.
    - Kullanıcı birisini takip etmeye başlarsa, takibi başlatır.
    - Kullanıcı birisini takibi bıraktığında, takibi sonlandırır.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        followed_user_id = request.data.get('followed_user_id')
        if not followed_user_id:
            return Response({"error": "Takip edilecek kullanıcı ID'si gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            followed_user = User.objects.get(id=followed_user_id)
        except User.DoesNotExist:
            return Response({"error": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

        # Kullanıcı zaten takip ediyor mu kontrol et
        follow_exists = Follow.objects.filter(user=request.user, followed_user=followed_user).exists()

        if follow_exists:
            # Kullanıcı zaten takip ediyorsa, takibi bırak
            Follow.objects.filter(user=request.user, followed_user=followed_user).delete()
            # Takip edilen kişinin follower sayısını azaltıyoruz
            followed_user.profile.followers.remove(request.user)
            followed_user.profile.save()
            return Response({"message": f"{followed_user.username} artık takip edilmemektedir."}, status=status.HTTP_200_OK)
        else:
            # Kullanıcı takip etmiyorsa, takibi başlat
            Follow.objects.create(user=request.user, followed_user=followed_user)
            # Takip edilen kişinin follower sayısını arttırıyoruz
            followed_user.profile.followers.add(request.user)
            followed_user.profile.save()
            return Response({"message": f"{followed_user.username} takip edilmeye başlandı."}, status=status.HTTP_201_CREATED)

class FollowedUsersView(APIView):
    def get(self, request):
        profile = request.user.profile
        followed_users = profile.following.all()
        serializer = ProfileSerializer(followed_users, many=True)  # ProfileSerializer yerine UserSerializer
        return Response(serializer.data)

class FollowersView(APIView):
    def get(self, request):
        profile = request.user.profile
        followers = profile.followers.all()
        serializer = ProfileSerializer(followers, many=True)  # ProfileSerializer yerine UserSerializer
        return Response(serializer.data)
