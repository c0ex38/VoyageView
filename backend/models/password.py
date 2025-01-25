from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *

class PasswordHistory(models.Model):
    """
    Kullanıcıların önceki şifrelerini saklar.
    
    Attributes:
        user: Şifrenin ait olduğu kullanıcı
        password_hash: Şifrenin hash'lenmiş hali
        created_at: Şifrenin oluşturulma tarihi
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Password History'
        verbose_name_plural = 'Password Histories'

    def __str__(self):
        return f"{self.user.username}'s password from {self.created_at}"