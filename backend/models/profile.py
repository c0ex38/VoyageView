from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *

class Profile(models.Model):
    """
    Profile modeli, bir kullanıcının profil bilgilerini tutar.
    Kullanıcıya ait kişisel bilgiler, biyografi, doğum tarihi, telefon numarası gibi alanların yanı sıra,
    sosyal bağlantılar, takipçi ve takip edilenler, seviye, puanlar ve rozetler gibi sosyal özellikler de saklanır.
    
    Alanlar:
    - user: Kullanıcıyı temsil eder. Her profil bir kullanıcıyla ilişkilendirilir.
    - is_email_verified: Kullanıcının e-posta adresinin doğrulanıp doğrulanmadığını belirtir.
    - bio: Kullanıcının biyografisini tutar. (isteğe bağlı)
    - location: Kullanıcının bulunduğu konumu tutar. (isteğe bağlı)
    - birth_date: Kullanıcının doğum tarihini tutar. (isteğe bağlı)
    - phone_number: Kullanıcının telefon numarasını tutar. (isteğe bağlı)
    - profile_image: Kullanıcının profil fotoğrafını tutar. (isteğe bağlı)
    - gender: Kullanıcının cinsiyetini tutar. 'M' (Erkek), 'F' (Kadın), 'O' (Diğer).
    - social_link: Kullanıcının sosyal medya bağlantısı. (isteğe bağlı)
    - created_at: Profilin oluşturulma tarihini tutar.
    - followers: Kullanıcının takipçilerini tutar. Birçok kullanıcı bir profilin takipçisi olabilir.
    - following: Kullanıcının takip ettiği profilleri tutar. Birçok kullanıcı bir profili takip edebilir.
    - level: Kullanıcının seviyesini tutar. Seviye, kullanıcının puanına göre belirlenir.
    - points: Kullanıcının toplam puanını tutar. Puanlar, kullanıcıların etkinliklerine göre artar.
    - badges: Kullanıcının kazandığı rozetleri tutar.
    
    Yöntemler:
    - __str__: Profilin kullanıcı adına göre bir string temsili döndürür.
    - update_level: Kullanıcının seviyesini günceller. Seviye, her 100 puanda bir artar.
    """
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")  # Kullanıcıyla birebir ilişki
    is_email_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    social_link = models.URLField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Takipçi ve takip edilenler arasındaki ManyToMany ilişkisi
    followers = models.ManyToManyField(User, related_name='following_profiles')  # Takip edenler
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers_profiles')  # Takip edilenler

    level = models.PositiveIntegerField(default=1, db_index=True)
    points = models.PositiveIntegerField(default=0, db_index=True)
    badges = models.ManyToManyField('Badge', related_name="users", blank=True)


    def __str__(self):
        """
        Kullanıcı adı ile profilin string temsili döndürülür.
        """
        return f"{self.user.username}'s Profile"

    def update_level(self):
        """
        Kullanıcının seviyesini, puanlarına göre günceller. 
        100 puan başına 1 seviye artar.
        """
        new_level = (self.points // 100) + 1  # 100 puan = 1 seviye
        if self.level != new_level:
            self.level = new_level
            self.save()  # Seviyeyi sadece değiştiğinde kaydediyoruz

class EmailVerification(models.Model):
    """
    EmailVerification modeli, bir kullanıcının e-posta adresinin doğrulama sürecini yönetir.
    Bu model, her kullanıcı için benzersiz bir doğrulama kodu tutar ve bu kodun ne zaman oluşturulduğunu izler.

    Alanlar:
    - user: Doğrulama kodunun ait olduğu kullanıcı. Her doğrulama kodu bir kullanıcıya aittir.
    - verification_code: Kullanıcıya gönderilen doğrulama kodu.
    - created_at: Doğrulama kodunun oluşturulma tarihi. Bu tarih, kodun ne kadar süreyle geçerli olduğunu kontrol etmek için kullanılır.
    
    Yöntemler:
    - __str__: Doğrulama kodunu içeren bir string temsili döndürür.
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Kullanıcı ile birebir ilişki
    verification_code = models.CharField(max_length=6)  # Doğrulama kodu (6 karakter)
    created_at = models.DateTimeField(default=now)  # Doğrulama kodunun oluşturulma zamanı

    def __str__(self):
        """
        Bu metod, doğrulama kodunu içeren bir string temsili döndürür.
        Örneğin: "Verification code for user_name: 123456"
        """
        return f"Verification code for {self.user.username}: {self.verification_code}"
