from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import Notification
from .serializers import NotificationSerializer
from .utils import send_push_notification

class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination

    def get(self, request):
        # Filtreleme parametreleri
        filter_type = request.query_params.get('type', None)
        is_read = request.query_params.get('is_read', None)
        time_frame = request.query_params.get('time_frame', None)

        notifications = Notification.objects.filter(user=request.user)

        # Tip filtrelemesi
        if filter_type:
            notifications = notifications.filter(notification_type=filter_type)

        # Okunma durumu filtrelemesi
        if is_read is not None:
            is_read = is_read.lower() == 'true'
            notifications = notifications.filter(is_read=is_read)

        # Zaman aralığı filtrelemesi
        if time_frame:
            now = timezone.now()
            if time_frame == 'today':
                notifications = notifications.filter(created_at__date=now.date())
            elif time_frame == 'week':
                notifications = notifications.filter(created_at__gte=now - timedelta(days=7))
            elif time_frame == 'month':
                notifications = notifications.filter(created_at__gte=now - timedelta(days=30))

        # Sıralama
        notifications = notifications.order_by('-created_at')

        # Sayfalama
        paginator = self.pagination_class()
        paginated_notifications = paginator.paginate_queryset(notifications, request)
        
        serializer = NotificationSerializer(paginated_notifications, many=True)
        
        # İstatistikler
        stats = {
            'total_unread': notifications.filter(is_read=False).count(),
            'total_notifications': notifications.count(),
        }
        
        return Response({
            'notifications': serializer.data,
            'stats': stats,
            'pagination': {
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'count': paginator.page.paginator.count
            }
        })

    def delete(self, request):
        """Toplu bildirim silme"""
        notification_ids = request.data.get('notification_ids', [])
        
        if not notification_ids:
            return Response({
                "error": "Silinecek bildirim ID'leri gerekli"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        deleted_count = Notification.objects.filter(
            user=request.user,
            id__in=notification_ids
        ).delete()[0]
        
        return Response({
            "message": f"{deleted_count} bildirim silindi",
            "deleted_count": deleted_count
        })

class MarkNotificationAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id=None):
        """Tek veya çoklu bildirim okundu işaretleme"""
        try:
            if notification_id:
                # Tek bildirim işaretleme
                notification = Notification.objects.get(
                    id=notification_id, 
                    user=request.user
                )
                notification.is_read = True
                notification.read_at = timezone.now()
                notification.save()
                
                return Response({
                    "message": "Bildirim okundu olarak işaretlendi.",
                    "notification": NotificationSerializer(notification).data
                })
            else:
                # Toplu bildirim işaretleme
                notification_ids = request.data.get('notification_ids', [])
                if not notification_ids:
                    # Tüm bildirimleri okundu işaretle
                    updated_count = Notification.objects.filter(
                        user=request.user,
                        is_read=False
                    ).update(
                        is_read=True,
                        read_at=timezone.now()
                    )
                else:
                    # Seçili bildirimleri okundu işaretle
                    updated_count = Notification.objects.filter(
                        user=request.user,
                        id__in=notification_ids,
                        is_read=False
                    ).update(
                        is_read=True,
                        read_at=timezone.now()
                    )
                
                return Response({
                    "message": f"{updated_count} bildirim okundu olarak işaretlendi."
                })
                
        except Notification.DoesNotExist:
            return Response({
                "error": "Bildirim bulunamadı."
            }, status=status.HTTP_404_NOT_FOUND)

class NotificationSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Kullanıcının bildirim ayarlarını getir"""
        user = request.user
        return Response({
            'email_notifications': user.notification_preferences.get('email', True),
            'push_notifications': user.notification_preferences.get('push', True),
            'notification_types': user.notification_preferences.get('types', {
                'comments': True,
                'likes': True,
                'follows': True,
                'mentions': True
            })
        })

    def put(self, request):
        """Bildirim ayarlarını güncelle"""
        user = request.user
        settings = request.data
        
        # Ayarları güncelle
        user.notification_preferences = {
            'email': settings.get('email_notifications', True),
            'push': settings.get('push_notifications', True),
            'types': settings.get('notification_types', {
                'comments': True,
                'likes': True,
                'follows': True,
                'mentions': True
            })
        }
        user.save()
        
        return Response({
            "message": "Bildirim ayarları güncellendi",
            "settings": user.notification_preferences
        })

class UnreadNotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Okunmamış bildirim sayısını getir"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({
            "unread_count": count
        })
