from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
from django.conf import settings

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=6, null=True, blank=True)
    password_reset_code = models.CharField(max_length=6, null=True, blank=True)
    password_reset_code = models.CharField(max_length=6, null=True, blank=True)
    
    # Konum bilgileri
    location = models.CharField(max_length=255, blank=True, default='Konum belirtilmedi')
    latitude = models.FloatField(null=True, blank=True, default=0.0)
    longitude = models.FloatField(null=True, blank=True, default=0.0)

    def __str__(self):
        return f"{self.username} - {self.location}"

class VerificationCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification_codes'
    )
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=[
        ('EMAIL', 'Email Verification'),
        ('PASSWORD', 'Password Reset'),
        ('2FA', 'Two Factor Authentication')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.purpose} - {self.code}"
    
    @classmethod
    def generate_code(cls):
        """6 haneli rastgele sayısal kod oluşturur"""
        return ''.join(random.choices(string.digits, k=6))
    
    @classmethod
    def create_verification_code(cls, user, purpose, expiry_minutes=30):
        """Yeni bir doğrulama kodu oluşturur"""
        code = cls.generate_code()
        expires_at = timezone.now() + timezone.timedelta(minutes=expiry_minutes)
        
        # Varolan aktif kodları iptal et
        cls.objects.filter(
            user=user,
            purpose=purpose,
            is_used=False,
            expires_at__gt=timezone.now()
        ).update(is_used=True)
        
        # Yeni kod oluştur
        verification_code = cls.objects.create(
            user=user,
            code=code,
            purpose=purpose,
            expires_at=expires_at
        )
        
        return verification_code
    
    def is_valid(self):
        """Kodun hala geçerli olup olmadığını kontrol eder"""
        return (
            not self.is_used and
            self.expires_at > timezone.now()
        )
    
    def use(self):
        """Kodu kullanılmış olarak işaretler"""
        self.is_used = True
        self.save()
