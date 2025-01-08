from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *

class GroupChat(models.Model):
    """
    GroupChat modeli, bir grup sohbetini temsil eder.
    Bu modelde grup adı, grup üyeleri, yöneticileri ve oluşturulma tarihi gibi bilgiler saklanır.
    
    Alanlar:
    - name: Grup sohbetinin adı.
    - members: Gruba ait üyeleri tutar. Bir grup birden fazla üyeye sahip olabilir.
    - admins: Grubun yöneticilerini tutar. Yöneticiler, grup yönetimi yapabilen kullanıcılardır.
    - created_at: Grubun oluşturulma tarihi. Grup oluşturulduğunda otomatik olarak belirlenir.
    
    Yöntemler:
    - __str__: Grup adını döndürür.
    """
    
    name = models.CharField(max_length=255)  # Grup sohbetinin adı
    members = models.ManyToManyField(User, related_name="group_chats")  # Grubun üyeleri
    admins = models.ManyToManyField(User, related_name="admin_groups")  # Grubun yöneticileri
    created_at = models.DateTimeField(auto_now_add=True)  # Grup sohbetinin oluşturulma tarihi

    def __str__(self):
        """
        Bu metod, grup sohbetinin adını döndürür. Yönetici paneli veya hata mesajlarında grup adı görüntülenebilir.
        """
        return self.name