from rest_framework import serializers, generics, permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from backend.models import Comment, Notification
from backend.serializers import CommentSerializer

class UserCommentListView(generics.ListAPIView):
    """
    Kullanıcının yaptığı tüm yorumları listeler.
    - Kullanıcı sadece kendi yorumlarını görüntüleyebilir.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]  # Sadece giriş yapmış kullanıcılar erişebilir

    def get_queryset(self):
        """
        Kullanıcının yaptığı yorumları döndürür.
        - Yalnızca giriş yapan kullanıcının yorumları döndürülür.
        """
        return Comment.objects.filter(author=self.request.user).order_by('-created_at')  # Kullanıcının yorumları, oluşturulma tarihine göre sıralanır

class UserLikedCommentsView(generics.ListAPIView):
    """
    Kullanıcının beğendiği tüm yorumları listeler.
    - Kullanıcı sadece beğendiği yorumları görüntüleyebilir.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]  # Sadece giriş yapmış kullanıcılar erişebilir

    def get_queryset(self):
        """
        Kullanıcının beğendiği yorumları döndürür.
        - Yalnızca giriş yapan kullanıcının beğendiği yorumlar döndürülür.
        """
        return Comment.objects.filter(likes=self.request.user).order_by('-created_at')  # Kullanıcının beğendiği yorumları, oluşturulma tarihine göre sıralar

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id, parent=None).order_by('-created_at')

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']  # post_id'yi URL parametresinden alıyoruz
        parent_id = self.request.data.get('parent', None)

        try:
            if parent_id:
                parent_comment = Comment.objects.get(id=parent_id)
                comment = serializer.save(author=self.request.user, post_id=post_id, parent=parent_comment)
            else:
                comment = serializer.save(author=self.request.user, post_id=post_id)

            # Bildirimler ekleyebilirsiniz burada
        except Comment.DoesNotExist:
            raise serializers.ValidationError({"error": "Parent comment not found."})

class CommentUpdateView(generics.UpdateAPIView):
    """
    Yalnızca kendi yorumlarını güncelleyebilen API.
    - Yorumun içeriği güncellenebilir.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Yalnızca kullanıcının yazdığı yorumları döndürür.
        """
        return Comment.objects.filter(author=self.request.user)

    def perform_update(self, serializer):
        """
        Kullanıcı sadece kendi yorumunu güncelleyebilir.
        """
        comment = self.get_object()  # Yorum objesini alıyoruz
        if comment.author != self.request.user:
            # Eğer kullanıcı, yorumun sahibi değilse, hata döndür
            return Response({"error": "Sadece kendi yorumunuzu güncelleyebilirsiniz."}, status=403)

        serializer.save()  # Yorum güncelleniyor

class CommentDestroyView(generics.DestroyAPIView):
    """
    Kullanıcının yazdığı yorumları veya kendi postlarına gelen yorumları silmesini sağlar.
    - Yorum yalnızca kullanıcının yazdığı yorumsa veya kullanıcının yazdığı postun yorumlarıysa silinebilir.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]  # Sadece giriş yapmış kullanıcılar yorum silebilir

    def get_queryset(self):
        """
        Kullanıcı, kendi yazdığı yorumları veya kendi yazdığı postlara gelen yorumları silebilir.
        """
        user = self.request.user
        # Kullanıcının yazdığı yorumlar ve kendi yazdığı postlara gelen yorumlar döndürülür.
        return Comment.objects.filter(author=user) | Comment.objects.filter(post__author=user)

    def destroy(self, request, *args, **kwargs):
        """
        Yorum silindiğinde, başarı mesajı ile birlikte 200 HTTP kodu döndürülür.
        """
        instance = self.get_object()  # Silinecek yorumu alıyoruz
        self.perform_destroy(instance)  # Yorum silme işlemi yapılır

        return Response({"message": "Yorum başarıyla silindi."}, status=status.HTTP_200_OK)

class CommentLikeToggleView(generics.GenericAPIView):
    """
    Yorum beğenme ve beğeniyi kaldırma işlemini gerçekleştirir.
    - Yorum beğenildiğinde, ilgili kullanıcıya bildirim gönderilir.
    """
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]  # Yalnızca giriş yapmış kullanıcılar beğenme işlemi yapabilir

    def post(self, request, pk, *args, **kwargs):
        """
        Yorumun beğenilmesi veya beğeninin kaldırılması işlemini yapar.
        - Beğenme işlemi sonrası güncel beğeni sayısını döndürür.
        - Yorum beğenildiğinde, yorum sahibine bildirim gönderilir.
        """
        try:
            comment = self.get_object()  # Yorumu alıyoruz
        except Comment.DoesNotExist:
            return Response({"error": "Yorum bulunamadı"}, status=status.HTTP_404_NOT_FOUND)

        if request.user in comment.likes.all():
            # Beğeni kaldırma işlemi yapılır
            comment.likes.remove(request.user)
            message = "Beğeni kaldırıldı"
        else:
            # Beğeni ekleme işlemi yapılır
            comment.likes.add(request.user)
            message = "Beğeni eklendi"

            # Bildirim: Yorum beğenildiğinde
            if comment.author != request.user:
                Notification.objects.create(
                    user=comment.author,  # Yorumun sahibi
                    sender=request.user,  # Beğeniyi yapan kullanıcı
                    notification_type='like',  # Bildirim tipi
                    comment=comment
                )

        # Güncel beğeni sayısını ve beğeni durumu döndürülür
        return Response({
            "message": message,
            "likes_count": comment.likes.count(),
            "is_liked": request.user in comment.likes.all()  # Kullanıcının bu yorumu beğenip beğenmediği durumu
        }, status=status.HTTP_200_OK)

