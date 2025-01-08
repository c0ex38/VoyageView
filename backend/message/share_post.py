from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from backend.models import SharedPost, Post, User
from backend.serializers import SharedPostSerializer
from backend.models import Notification

class SharePostView(generics.CreateAPIView):
    """
    Kullanıcının bir postu başkasına paylaşmasını sağlayan API.
    - Post ve alıcı doğrulandıktan sonra, paylaşım kaydedilir ve ilgili alıcıya bildirim gönderilir.
    """
    serializer_class = SharedPostSerializer
    permission_classes = [permissions.IsAuthenticated]  # Sadece giriş yapmış kullanıcılar post paylaşabilir

    def perform_create(self, serializer):
        """
        Paylaşılacak postu ve alıcıyı doğrular, postu kaydeder ve ilgili alıcıya bildirim gönderir.
        """
        post_id = self.request.data.get('post_id')
        recipient_id = self.request.data.get('recipient_id')
        message = self.request.data.get('message', '')  # Mesaj optional (isteğe bağlı)

        # Post ve alıcıyı doğrula
        post = get_object_or_404(Post, id=post_id)
        recipient = get_object_or_404(User, id=recipient_id)

        # Post paylaşımını kaydet
        serializer.save(
            sender=self.request.user,
            post=post,
            recipient=recipient,
            message=message
        )

        # Paylaşım bildirimini oluştur
        if recipient != self.request.user:
            Notification.objects.create(
                user=recipient,  # Alıcıya bildirim gönderilir
                sender=self.request.user,  # Paylaşan kullanıcı
                notification_type='post_share',  # Bildirim tipi
                post=post  # Paylaşılan post
            )

    def post(self, request, *args, **kwargs):
        """
        Paylaşım başarılı olduğunda, kullanıcıya başarı mesajı döndürülür.
        """
        response = super().post(request, *args, **kwargs)
        return Response(
            {"message": "Post başarıyla paylaşıldı!", "data": response.data},  # Başarı mesajı Türkçe olarak döndürülür
            status=status.HTTP_201_CREATED
        )
