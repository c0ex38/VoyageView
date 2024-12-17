from rest_framework import generics, permissions, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from backend.models import Post
from backend.serializers import PostSerializer
from django.db import models
from backend.permissions import IsOwner

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']  # Kategoriye göre filtreleme
    search_fields = ['title', 'description', 'location']  # Arama yapılacak alanlar
    ordering_fields = ['likes_count', 'created_at']  # Sıralanacak alanlar
    ordering = ['-created_at']  # Varsayılan sıralama

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(likes_count=models.Count('likes'))  # Beğeni sayısını hesapla

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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

        return Response({"message": message, "likes_count": post.likes.count()}, status=status.HTTP_200_OK)


class FollowedUsersPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]  # Yetkilendirme zorunlu

    def get_queryset(self):
        user = self.request.user
        # Takip edilen kullanıcıların postlarını filtrele
        followed_users = user.profile.following.all().values_list('user', flat=True)
        return Post.objects.filter(author__in=followed_users).order_by('-created_at')