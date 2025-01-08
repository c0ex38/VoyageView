from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *
from .post import Post

class Comment(models.Model):
    """
    Comment modeli, bir gönderiye yapılan yorumları temsil eder.
    
    Her yorum, bir kullanıcı tarafından yazılır ve bir gönderiye aittir. Yorumlar bir başka yoruma cevap olarak yazılabilir
    ve kullanıcılar yorumları beğenebilir. 
    
    Alanlar:
    - post: Yorumun ait olduğu gönderiyi belirtir. Yani hangi gönderiye yapıldığını gösterir.
    - author: Yorumun yazarı kimdir? Bu alanda yorumun yazıldığı kullanıcı belirtilir.
    - content: Yorumun içeriği burada tutulur. Yorumun metni, kullanıcının gönderdiği yazılı mesajdır.
    - parent: Eğer bu yorum bir cevapsa, o zaman hangi yoruma cevaben yazıldığını belirtir. Yorumun bir başka yoruma yanıt olup olmadığını gösterir.
    - likes: Hangi kullanıcılar bu yorumu beğenmiş? Birçok kullanıcı bir yorumu beğenebilir.
    - created_at: Yorumun oluşturulma tarih ve saatini belirtir. Yorum ne zaman yapıldı?
    - edited_at: Yorumun ne zaman düzenlendiği bilgisini tutar.
    - like_count: Yorumun toplam beğeni sayısını tutar.
    """
    post = models.ForeignKey(Post, related_name='comments_related', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)  # Beğeni alanı
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)  # Yorumun düzenlendiği tarih
    like_count = models.PositiveIntegerField(default=0)  # Beğeni sayısı
    
    def edit(self, new_content):
        self.content = new_content
        self.edited_at = timezone.now()
        self.save()

    def update_like_count(self):
        """Beğeni sayısını günceller."""
        self.like_count = self.likes.count()
        self.save()

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"