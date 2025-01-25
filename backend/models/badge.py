from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *

class Badge(models.Model):
    """
    Badge modeli, bir kullanıcının kazanabileceği rozetleri temsil eder. Rozetler,
    belirli başarılar veya seviyeler ile ödüllendirmek için kullanılır.

    Alanlar:
    - name: Rozetin adı, benzersiz olmalıdır.
    - description: Rozetin açıklaması, kullanıcılara rozetin neyle ilgili olduğunu anlatan bir metin.
    - level_requirement: Bu rozeti kazanmak için gereken seviye.
    - icon: Rozet simgesi, bu görsel kullanıcılara rozetin görsel temsilini sağlar.
    
    Yöntemler:
    - __str__: Rozetin adını ve seviyesini döndürür, böylece yönetici paneli ve diğer alanlarda kolayca tanınabilir.
    """
    
    name = models.CharField(max_length=50, unique=True)  # Rozet adı
    description = models.TextField(blank=True, null=True)  # Rozet açıklaması (isteğe bağlı)
    level_requirement = models.PositiveIntegerField()  # Seviyeye göre gereklilik
    icon = models.ImageField(upload_to='badge_icons/', blank=True, null=True)  # Rozet simgesi (isteğe bağlı)
    badge_type = models.CharField(
        max_length=50,
        choices=[('achievement', 'Achievement'), ('activity', 'Activity')],
        default='achievement'  # Varsayılan değer ekleyin
    )

    def __str__(self):
        """
        Bu metod, rozetin adını ve seviyesini döndürür. Bu, rozetin yönetici panelinde
        ve kullanıcı arayüzünde tanınmasını kolaylaştırır.
        """
        return f"{self.name} (Level {self.level_requirement})"