from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from backend.models import Message, User
from backend.serializers import MessageSerializer

class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['content', 'sender__username', 'recipient__username']

    def get_queryset(self):
        return Message.objects.filter(recipient=self.request.user)

    def perform_create(self, serializer):
        recipient_id = self.request.data.get("recipient")
        if not recipient_id:
            raise serializers.ValidationError({"recipient": "Recipient is required."})

        recipient = get_object_or_404(User, id=recipient_id)
        serializer.save(sender=self.request.user, recipient=recipient)


class MessageMarkAsReadView(generics.UpdateAPIView):
    queryset = Message.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        message = self.get_object()
        if message.recipient != request.user:
            return Response({"error": "You do not have permission to mark this message as read."}, status=403)
        message.is_read = True
        message.save()
        return Response({"message": "Message marked as read."})


class ArchiveMessageView(generics.UpdateAPIView):
    queryset = Message.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        message = self.get_object()
        if message.recipient != request.user:
            return Response({"error": "Permission denied."}, status=403)
        message.is_archived = True
        message.save()
        return Response({"message": "Message archived successfully."})


class SortedMessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['created_at', 'is_read', 'sender__username']

    def get_queryset(self):
        return Message.objects.filter(recipient=self.request.user)
