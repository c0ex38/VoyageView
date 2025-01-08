from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *

class Message(models.Model):
    """
    Message modeli, bir kullanıcı tarafından başka bir kullanıcıya gönderilen mesajları temsil eder.
    Bu model, mesajın göndereni, alıcısı, içeriği, mesaj durumu (okundu mu, arşivlendi mi), 
    ekli dosyalar ve mesajın oluşturulma zamanı gibi bilgileri saklar.
    
    Alanlar:
    - sender: Mesajı gönderen kullanıcı. Bu, mesajın sahibi olan kullanıcıyı belirtir.
    - recipient: Mesajı alan kullanıcı. Bu, mesajın alıcı kullanıcıyı belirtir.
    - content: Mesajın içeriği. Bu, mesajın yazılı kısmıdır.
    - created_at: Mesajın oluşturulma tarihi.
    - is_read: Mesaj okunmuş mu? Varsayılan olarak 'False' (okunmamış).
    - is_archived: Mesaj arşivlenmiş mi? Varsayılan olarak 'False'.
    - attachment: Mesaja eklenen dosya (isteğe bağlı).
    
    Yöntemler:
    - __str__: Mesajın göndereni, alıcısı ve oluşturulma zamanını içeren bir string temsili döndürür.
    """
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")  # Gönderen kullanıcı
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")  # Alıcı kullanıcı
    content = models.TextField()  # Mesajın içeriği
    created_at = models.DateTimeField(auto_now_add=True)  # Mesajın oluşturulma tarihi
    is_read = models.BooleanField(default=False)  # Mesaj okundu mu?
    is_archived = models.BooleanField(default=False)  # Mesaj arşivlendi mi?
    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)  # Mesaja ekli dosya (isteğe bağlı)

    def __str__(self):
        """
        Bu metod, mesajın string temsiline, mesajın göndereni, alıcısı ve oluşturulma zamanını içerir.
        Örneğin: "Message from User1 to User2 at 2023-01-01 12:00:00"
        """
        return f"Message from {self.sender} to {self.recipient} at {self.created_at}"
