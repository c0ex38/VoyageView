from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from backend.models import SharedPost, Post, User
from backend.serializers import SharedPostSerializer
from backend.models import Notification

class SharePostView(generics.CreateAPIView):
    serializer_class = SharedPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.request.data.get('post_id')
        recipient_id = self.request.data.get('recipient_id')
        message = self.request.data.get('message', '')

        # Post ve alıcıyı doğrula
        post = get_object_or_404(Post, id=post_id)
        recipient = get_object_or_404(User, id=recipient_id)

        # Post paylaşımı kaydet
        serializer.save(
            sender=self.request.user,
            post=post,
            recipient=recipient,
            message=message
        )

        # Bildirim oluştur
        if recipient != self.request.user:
            Notification.objects.create(
                user=recipient,
                sender=self.request.user,
                notification_type='post_share',
                post=post
            )

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response(
            {"message": "Post successfully shared!", "data": response.data},
            status=status.HTTP_201_CREATED
        )
