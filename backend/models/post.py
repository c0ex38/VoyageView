from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *

class Post(models.Model):
    """
    Post modeli, bir gönderinin tüm bilgilerini tutar. Bu modelde, bir kullanıcının
    belirli bir konumda ve kategoride paylaştığı gönderiye ait başlık, açıklama, 
    görsel, kategori, konum bilgisi, beğeni, oluşturulma tarihi ve etiketler gibi alanlar bulunur.
    
    Alanlar:
    - title: Gönderinin başlığını tutar.
    - description: Gönderinin açıklaması, isteğe bağlıdır.
    - image: Gönderiye ait görsel dosyası.
    - category: Gönderinin ait olduğu kategori, örneğin kültürel yer, turistik yer vb.
    - location_name: Gönderinin konumunun adı (örneğin, şehir adı veya bölge adı).
    - author: Gönderiyi paylaşan kullanıcıyı belirtir.
    - latitude: Gönderinin konumunun enlem bilgisini tutar.
    - longitude: Gönderinin konumunun boylam bilgisini tutar.
    - likes: Gönderiye beğeni yapan kullanıcıları tutar. Bir gönderi birden fazla kullanıcı tarafından beğenilebilir.
    - like_count: Beğeni sayısını tutar.
    - created_at: Gönderinin oluşturulma tarihini tutar.
    - updated_at: Gönderinin son güncellenme tarihini tutar.
    - tags: Gönderiye ait etiketler. Bir gönderi birden fazla etikete sahip olabilir.
    - comments: Gönderiye yapılan yorumları tutar.
    - media_type: Gönderinin medya türünü belirtir. (görsel, video, ses vb.)
    - status: Gönderinin yayın durumu (taslak, yayımlandı).
    - published_at: Gönderinin yayımlandığı tarih.
    - visibility: Gönderinin kimler tarafından görülebileceğini belirtir (genel, takipçiler, özel).
    """
    
    CATEGORY_CHOICES = [
        ('cultural', 'Cultural Place'),
        ('touristic', 'Touristic Place'),
        ('technology', 'Technology'),
        ('sports', 'Sports'),
        ('art', 'Art'),
        ('nature', 'Nature'),
        ('historical', 'Historical Sites'),
        ('educational', 'Educational Institutions'),
        ('entertainment', 'Entertainment'),
        ('music', 'Music'),
        ('food', 'Food & Drink'),
        ('adventure', 'Adventure'),
        ('wellness', 'Wellness'),
        ('shopping', 'Shopping'),
        ('business', 'Business'),
        ('lifestyle', 'Lifestyle'),
        ('festival', 'Festival'),
        ('nightlife', 'Nightlife'),
        ('outdoor', 'Outdoor Activities'),
        ('religious', 'Religious Sites'),
        ('romantic', 'Romantic Getaways'),
        ('family', 'Family Activities'),
    ]

    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('followers', 'Followers Only'),
        ('private', 'Private'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=255)  # Gönderinin başlığı
    description = models.TextField(blank=True, null=True)  # Gönderinin açıklaması (isteğe bağlı)
    image = models.ImageField(upload_to='post_images/', blank=False, null=False)  # Gönderiye ait görsel dosyası
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)  # Gönderinin kategorisi
    location_name = models.CharField(max_length=255, db_index=True)  # Konum adı (örneğin, şehir adı)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")  # Gönderiyi paylaşan kullanıcı
    latitude = models.FloatField(blank=False, null=False)  # Gönderinin enlem bilgisi
    longitude = models.FloatField(blank=False, null=False)  # Gönderinin boylam bilgisi
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)  # Gönderiye beğeni yapan kullanıcılar
    like_count = models.PositiveIntegerField(default=0)  # Beğeni sayısı
    created_at = models.DateTimeField(auto_now_add=True)  # Gönderinin oluşturulma tarihi
    updated_at = models.DateTimeField(auto_now=True)  # Gönderinin son güncellenme tarihi
    tags = models.ManyToManyField('Tag', related_name='posts', blank=True)  # Gönderiye ait etiketler
    comments = models.ManyToManyField('Comment', related_name='posts_related', blank=True)  # Gönderiye yapılan yorumlar
    media_type = models.CharField(
            max_length=20, 
            choices=[('image', 'Image'), ('video', 'Video'), ('audio', 'Audio')],
            default='image'  # Varsayılan değer olarak 'image' eklendi
        )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')  # Yayın durumu
    published_at = models.DateTimeField(null=True, blank=True)  # Yayınlanma tarihi
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')  # Gönderi görünürlüğü

    def location(self):
        """
        Gönderinin enlem ve boylam bilgisini birleştirir.
        """
        return f"{self.latitude}, {self.longitude}"

    def update_like_count(self):
        """Beğeni sayısını günceller."""
        self.like_count = self.likes.count()
        self.save()

    def __str__(self):
        """
        Gönderinin başlığını döndürür.
        """
        return self.title