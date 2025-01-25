from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *

class Notification(models.Model):
    """
    Notification modeli, bir kullanıcının aldığı bildirimleri tutar. 
    Bildirimler, belirli bir etkinlik (beğeni, yorum, takip) ile ilgili olarak oluşturulur ve kullanıcıya bildirilir.
    
    Alanlar:
    - user: Bildirimin alıcısı (kullanıcı).
    - sender: Bildirimi gönderen kullanıcı.
    - notification_type: Bildirimin türü, 'like' (beğeni), 'comment' (yorum), 'follow' (takip) gibi seçenekler.
    - post: İlgili gönderiyi belirtir. Yalnızca 'like' ve 'comment' türleri için geçerli olabilir.
    - comment: İlgili yorumu belirtir. Yalnızca 'comment' türü için geçerli olabilir.
    - is_read: Kullanıcı bildirimi okudu mu? Varsayılan olarak 'False' (okunmamış).
    - created_at: Bildirimin oluşturulma tarihi.
    
    Yöntemler:
    - __str__: Bildirimin alıcısını ve göndereni belirterek bildirimin bir string temsili döndürür.
    """
    
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')  # Bildirimi alan kullanıcı
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')  # Bildirimi gönderen kullanıcı
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)  # Bildirimin türü
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)  # İlgili gönderi (beğeni ve yorum için)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)  # İlgili yorum (yalnızca yorum bildirimi için)
    is_read = models.BooleanField(default=False)  # Bildirim okundu mu?
    created_at = models.DateTimeField(auto_now_add=True)  # Bildirimin oluşturulma tarihi

    def __str__(self):
        """
        Bu metod, bildirim oluşturulduğunda bildirimin alıcısını ve göndereni belirten bir string temsili döndürür.
        """
        return f"Notification for {self.user.username} from {self.sender.username}"