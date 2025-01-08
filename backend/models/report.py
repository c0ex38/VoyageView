from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *

class Report(models.Model):
    """
    Report modeli, kullanıcıların içerikleri raporlamak için kullandığı yapıyı temsil eder.
    Bu model, içeriklerin kullanıcılar tarafından çeşitli sebeplerle raporlanmasını takip eder.
    
    Alanlar:
    - user: Raporu gönderen kullanıcı.
    - report_type: Rapor edilen içeriğin türü (Gönderi, Yorum, Kullanıcı).
    - reason: Raporlanma sebebi (Spam, Taciz, Uygunsuz içerik vb.).
    - post: Rapor edilen gönderiyi belirtir. (Yalnızca 'post' türü için geçerlidir.)
    - comment: Rapor edilen yorumu belirtir. (Yalnızca 'comment' türü için geçerlidir.)
    - status: Raporun mevcut durumu (Bekliyor, İnceleniyor, Çözüldü, Reddedildi).
    - detailed_description: Kullanıcının raporla ilgili eklediği açıklama.
    - created_at: Raporun oluşturulma tarihi.
    - updated_at: Raporun son güncellenme tarihi.

    Yöntemler:
    - __str__: Raporun temel bilgilerini döndürür. Örneğin: "Post Report by UserName - Pending".
    - clean: Raporun geçerli olması için ya bir gönderiye ya da bir yoruma bağlanması gerektiğini kontrol eder.
    """
    
    REPORT_TYPES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
        ('user', 'User'),
    ]

    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('abuse', 'Abuse'),
        ('inappropriate', 'Inappropriate Content'),
        ('harassment', 'Harassment'),  # Yeni rapor sebebi ekledik
        ('fake', 'Fake Account or Content')  # Yeni bir sebep ekledik
    ]

    REPORT_STATUSES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')  # Raporu gönderen kullanıcı
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)  # Rapor edilen içeriğin türü
    reason = models.CharField(max_length=50, choices=REPORT_REASONS)  # Rapor sebebi
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)  # İlgili gönderi (eğer varsa)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)  # İlgili yorum (eğer varsa)
    status = models.CharField(max_length=20, choices=REPORT_STATUSES, default='pending')  # Rapor durumu
    detailed_description = models.TextField(null=True, blank=True)  # Kullanıcının ek açıklaması
    created_at = models.DateTimeField(auto_now_add=True)  # Rapor oluşturulma tarihi
    updated_at = models.DateTimeField(auto_now=True)  # Rapor güncellenme tarihi

    def clean(self):
        """
        Raporun geçerli olması için ya bir gönderiye ya da bir yoruma bağlanması gerektiğini kontrol eder.
        Eğer her ikisi de boşsa, ValidationError fırlatılır.
        """
        if not self.post and not self.comment:
            raise ValidationError("A report must be associated with either a post or a comment.")
    
    def __str__(self):
        """
        Bu metod, raporun türünü, raporu gönderen kullanıcıyı ve raporun durumunu döndürür.
        Örneğin: "Post Report by UserName - Pending"
        """
        return f"{self.report_type.capitalize()} Report by {self.user.username} - {self.get_status_display()}"

    class Meta:
        """
        Raporlar, oluşturulma tarihine göre azalan sırayla sıralanır.
        """
        ordering = ['-created_at']  # En yeni raporlar üstte görünsün
        
