from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import NotificationSerializer

def create_notification(user, message, notification_type='INFO'):
    """
    Kullanıcı için yeni bir bildirim oluşturur
    """
    from .models import Notification
    
    return Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type
    )

def send_realtime_notification(notification):
    """
    WebSocket üzerinden real-time bildirim gönder
    """
    channel_layer = get_channel_layer()
    notification_data = NotificationSerializer(notification).data
    
    async_to_sync(channel_layer.group_send)(
        f'notifications_{notification.user.id}',
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )

def send_push_notification(user, title, message, data=None):
    """
    Push notification gönderme fonksiyonu
    İleride bir push notification servisi eklemek isterseniz 
    bu fonksiyonu kullanabilirsiniz
    """
    try:
        # Şimdilik sadece log atalım
        print(f"Push notification would be sent to {user.username}")
        print(f"Title: {title}")
        print(f"Message: {message}")
        print(f"Data: {data}")
        
        # Firebase veya başka bir push notification servisi eklenebilir
        # firebase_admin.messaging.send(...)
        
        return True
    except Exception as e:
        print(f"Push notification error: {e}")
        return False

def get_notification_settings(user):
    """
    Kullanıcının bildirim ayarlarını getirir
    """
    return {
        'email_notifications': user.notification_preferences.get('email', True),
        'push_notifications': user.notification_preferences.get('push', True),
        'notification_types': user.notification_preferences.get('types', {
            'comments': True,
            'likes': True,
            'follows': True,
            'mentions': True
        })
    }

def should_send_notification(user, notification_type):
    """
    Kullanıcının belirli bir bildirim türü için bildirim alıp almaması gerektiğini kontrol eder
    """
    settings = get_notification_settings(user)
    return settings['notification_types'].get(notification_type, True)
