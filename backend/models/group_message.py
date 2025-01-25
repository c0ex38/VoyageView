from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *
from .group_chat import GroupChat

class GroupMessage(models.Model):
    """
    GroupMessage modeli, grup sohbetlerinde gönderilen mesajları temsil eder.
    Her mesaj, bir grup sohbetine, bir gönderen kullanıcıya, mesaj içeriğine
    ve mesajın oluşturulma zamanına sahiptir.

    Alanlar:
    - group: Mesajın ait olduğu grup sohbeti. Bir grup sohbetinde birden fazla mesaj olabilir.
    - sender: Mesajı gönderen kullanıcı. Her mesaj bir kullanıcıya aittir.
    - content: Mesajın içeriği. Bu, gönderilen yazılı mesajdır.
    - created_at: Mesajın oluşturulma tarihi. Bu, mesajın ne zaman gönderildiğini belirler.

    Yöntemler:
    - __str__: Mesajın string temsili döndürülür. Bu, mesajın içeriği ve göndereni hakkında bilgi sağlar.
    """
    
    group = models.ForeignKey(GroupChat, related_name="messages", on_delete=models.CASCADE)  # Mesajın ait olduğu grup
    sender = models.ForeignKey(User, on_delete=models.CASCADE)  # Mesajı gönderen kullanıcı
    content = models.TextField()  # Mesajın içeriği
    created_at = models.DateTimeField(auto_now_add=True)  # Mesajın oluşturulma tarihi

    def __str__(self):
        """
        Bu metod, mesajın string temsiline, mesajın içeriğini ve gönderen kullanıcıyı dahil eder.
        Örneğin: "Message from UserName: Hello!"
        """
        return f"Message from {self.sender.username}: {self.content[:50]}..."  # İçeriğin ilk 50 karakteri döndürülür