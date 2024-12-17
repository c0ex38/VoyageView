from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from backend.models import Comment
from backend.serializers import CommentSerializer

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination  # Sayfalandırma eklendi

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id, parent=None).order_by('-created_at')

    def perform_create(self, serializer):
        parent_id = self.request.data.get('parent', None)
        post_id = self.kwargs['post_id']

        if parent_id:
            parent_comment = Comment.objects.get(id=parent_id)
            serializer.save(author=self.request.user, post_id=post_id, parent=parent_comment)
        else:
            serializer.save(author=self.request.user, post_id=post_id)


class CommentDestroyView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)


class CommentLikeToggleView(generics.GenericAPIView):
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        comment = self.get_object()
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
            message = "Like removed"
        else:
            comment.likes.add(request.user)
            message = "Like added"

        return Response({"message": message, "likes_count": comment.likes.count()}, status=status.HTTP_200_OK)