from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from backend.models import Message, User
from backend.serializers import MessageSerializer

class MessageListCreateView(generics.ListCreateAPIView):
    """
    Kullanıcıların mesajlarını listeleme ve oluşturma işlemi yapan API.
    - Kullanıcı yalnızca kendi aldığı mesajları görebilir.
    - Yeni mesajlar gönderebilir.
    """
    queryset = Message.objects.all()  # Tüm mesajları alıyoruz
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]  # Yalnızca giriş yapmış kullanıcılar erişebilir
    search_fields = ['content', 'sender__username', 'recipient__username']  # Mesaj içerikleri ve kullanıcı adları üzerinden arama yapılabilir

    def get_queryset(self):
        """
        Kullanıcının aldığı mesajları döndürür.
        - Yalnızca giriş yapmış kullanıcının almış olduğu mesajlar listeye döndürülür.
        """
        return Message.objects.filter(recipient=self.request.user)

    def perform_create(self, serializer):
        """
        Yeni mesaj oluşturulurken alıcıyı kontrol eder ve mesajı kaydeder.
        - Alıcı kullanıcı geçerli değilse hata mesajı döndürülür.
        """
        recipient_id = self.request.data.get("recipient")
        if not recipient_id:
            raise serializers.ValidationError({"recipient": "Alıcı gereklidir."})

        recipient = get_object_or_404(User, id=recipient_id)
        serializer.save(sender=self.request.user, recipient=recipient)


class MessageMarkAsReadView(generics.UpdateAPIView):
    """
    Kullanıcının mesajlarını okundu olarak işaretleme işlemi yapan API.
    - Sadece alıcı kullanıcı bu işlemi gerçekleştirebilir.
    """
    queryset = Message.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """
        Mesajı okundu olarak işaretler.
        - Kullanıcı, yalnızca kendisine ait mesajları okundu olarak işaretleyebilir.
        """
        message = self.get_object()
        if message.recipient != request.user:
            return Response({"hata": "Bu mesajı okundu olarak işaretleme izniniz yok."}, status=403)
        message.is_read = True
        message.save()
        return Response({"mesaj": "Mesaj başarıyla okundu olarak işaretlendi."})


class ArchiveMessageView(generics.UpdateAPIView):
    """
    Kullanıcının mesajlarını arşivleme işlemi yapan API.
    - Sadece alıcı kullanıcı bu işlemi gerçekleştirebilir.
    """
    queryset = Message.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """
        Mesajı arşivler.
        - Kullanıcı yalnızca kendisine ait mesajları arşivleyebilir.
        """
        message = self.get_object()
        if message.recipient != request.user:
            return Response({"hata": "İzin verilmedi."}, status=403)
        message.is_archived = True
        message.save()
        return Response({"mesaj": "Mesaj başarıyla arşivlendi."})


class SortedMessageListView(generics.ListAPIView):
    """
    Kullanıcının mesajlarını sıralı bir şekilde listeleyen API.
    - Mesajlar, belirtilen sıralama kriterlerine göre sıralanır.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['created_at', 'is_read', 'sender__username']  # Sıralama yapılabilecek alanlar

    def get_queryset(self):
        """
        Kullanıcının aldığı mesajları belirtilen sıralama kriterine göre döndürür.
        """
        return Message.objects.filter(recipient=self.request.user)
