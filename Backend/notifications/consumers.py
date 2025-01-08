import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.user_id = str(self.scope["user"].id)
        self.notification_group_name = f'notifications_{self.user_id}'

        # Kullanıcıyı kendi grubuna ekle
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Bağlantı başarılı mesajı gönder
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Realtime notification connection established'
        }))

    async def disconnect(self, close_code):
        # Gruptan çıkar
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Client'tan gelen mesajları işle
        """
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'mark_as_read':
                notification_id = text_data_json.get('notification_id')
                success = await self.mark_notification_as_read(notification_id)
                
                await self.send(text_data=json.dumps({
                    'type': 'notification_marked_as_read',
                    'notification_id': notification_id,
                    'success': success
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def notification_message(self, event):
        """
        Yeni bildirim geldiğinde çalışır
        """
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))

    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        from .models import Notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user_id=self.scope["user"].id
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
