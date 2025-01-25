from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import Notification
from backend.serializers import NotificationSerializer
from backend.permissions import IsNotificationOwner

class NotificationListView(generics.ListAPIView):
    """
    Kullanıcıya ait tüm bildirimleri listeleyen endpoint.
    - Giriş yapmış kullanıcının tüm bildirimlerini listeler.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Kullanıcıya ait tüm bildirimleri tarihe göre sıralar (en son bildirimler en üstte).
        """
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class NotificationMarkAsReadView(generics.UpdateAPIView):
    """
    Tek bir bildirimi okundu olarak işaretleyen endpoint.
    - Kullanıcı yalnızca kendisine ait bildirimleri okundu olarak işaretleyebilir.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotificationOwner]

    def patch(self, request, *args, **kwargs):
        """
        Bildirimi okundu olarak işaretler.
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"message": "Bildirim okundu olarak işaretlendi.", "notification_id": notification.id}, status=status.HTTP_200_OK)


class NotificationMarkAllAsReadView(APIView):
    """
    Kullanıcının tüm bildirimlerini toplu olarak okundu işaretleyen endpoint.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """
        Kullanıcının tüm okunmamış bildirimlerini okundu olarak işaretler.
        """
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        updated_count = notifications.update(is_read=True)
        return Response({"message": f"{updated_count} bildirim okundu olarak işaretlendi."}, status=status.HTTP_200_OK)


class NotificationUnreadCountView(APIView):
    """
    Kullanıcının okunmamış bildirim sayısını dönen endpoint.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Kullanıcının okunmamış bildirim sayısını döndürür.
        """
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)
