from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from backend.models import Profile, Post, Comment

class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.profile

        # Kullanıcı etkileşimleri
        total_posts = Post.objects.filter(author=user).count()
        total_comments = Comment.objects.filter(author=user).count()
        total_likes = Post.objects.filter(author=user).aggregate(Sum('likes')).get('likes__sum', 0)

        # Genel metrikler
        followers = profile.followers.count()
        following = profile.following.count()

        return Response({
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_likes": total_likes or 0,
            "followers": followers,
            "following": following,
        })
