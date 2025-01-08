from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *
from .post import Post

class PostMedia(models.Model):
    """
    PostMedia modeli, gönderilere ait medya dosyalarını (görseller ve videolar) temsil eder.
    
    Bu model, bir gönderiye ait medya dosyasının türünü ve dosyasını saklar. Ayrıca, medya dosyasının
    türüne göre (resim ya da video) belirli kısıtlamalar uygulanır, örneğin sadece belirli dosya uzantılarına izin verilir.
    
    Alanlar:
    - post: Bu medya dosyasının hangi gönderiye ait olduğunu belirtir. Bir gönderinin birden fazla medya dosyası olabilir.
    - media_type: Medya dosyasının türünü belirtir. Bu, 'image' (resim) ya da 'video' (video) olabilir.
    - file: Medya dosyasının kendisini tutar. Burada resim veya video dosyası saklanır.
    - created_at: Medya dosyasının oluşturulma tarih ve saatini belirtir. Bu, dosyanın yüklenme zamanını gösterir.
    
    Yöntemler:
    - clean: Medya türü video ise, dosyanın süresi doğrulanır.
    """
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    file = models.FileField(upload_to='post_media/', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi'])  # Yalnızca belirli uzantılara izin ver
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """
        Eğer medya türü video ise, video dosyasının süresi doğrulanır.
        """
        if self.media_type == 'video':
            validate_video_duration(self.file)

    def __str__(self):
        return f"{self.media_type} for Post {self.post.title}"