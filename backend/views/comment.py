from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from backend.models import Comment, Notification
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

        try:
            # Alt yorum kontrolü
            if parent_id:
                parent_comment = Comment.objects.get(id=parent_id)
                comment = serializer.save(author=self.request.user, post_id=post_id, parent=parent_comment)

                # Alt yorum bildirimi
                if parent_comment.author != self.request.user:
                    Notification.objects.create(
                        user=parent_comment.author,
                        sender=self.request.user,
                        notification_type='comment',
                        comment=comment
                    )
            else:
                # Ana yorum oluşturma
                comment = serializer.save(author=self.request.user, post_id=post_id)

                # Post sahibine bildirim
                post_author = comment.post.author
                if post_author != self.request.user:
                    Notification.objects.create(
                        user=post_author,
                        sender=self.request.user,
                        notification_type='comment',
                        post=comment.post
                    )
        except Comment.DoesNotExist:
            raise serializers.ValidationError({"error": "Parent comment does not exist"})

class CommentDestroyView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

class CommentLikeToggleView(generics.GenericAPIView):
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        try:
            comment = self.get_object()
        except Comment.DoesNotExist:
            return Response({"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if request.user in comment.likes.all():
            # Beğeni kaldırma işlemi
            comment.likes.remove(request.user)
            message = "Like removed"
        else:
            # Beğeni ekleme işlemi
            comment.likes.add(request.user)
            message = "Like added"

            # Bildirim: Yorum beğenildiğinde
            if comment.author != request.user:
                Notification.objects.create(
                    user=comment.author,  # Yorumun sahibi
                    sender=request.user,  # Beğeniyi yapan kullanıcı
                    notification_type='like',  # Bildirim tipi
                    comment=comment
                )

        # Güncel beğeni sayısını döndür
        return Response({
            "message": message,
            "likes_count": comment.likes.count()
        }, status=status.HTTP_200_OK)