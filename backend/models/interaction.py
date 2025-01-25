from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *
from .post import Post

class UserInteraction(models.Model):
    """
    UserInteraction modeli, kullanıcıların gönderilere yaptığı etkileşimleri (beğeni, yorum, görüntüleme) takip etmek için kullanılır.
    
    Bu modelde her etkileşim bir kullanıcı, bir gönderi ve etkileşim türü ile ilişkilidir.
    Kullanıcı bir gönderiye beğeni, yorum veya sadece görüntüleme yapabilir. 
    
    Alanlar:
    - user: Etkileşimi yapan kullanıcıyı belirtir. Hangi kullanıcı bu gönderiye etkileşimde bulunmuştur?
    - post: Hangi gönderiye etkileşimde bulunulduğunu belirtir. Bu, etkileşimin ait olduğu gönderiyi gösterir.
    - interaction_type: Etkileşimin türünü belirtir. Kullanıcı 'like' (beğeni), 'comment' (yorum) ya da 'view' (görüntüleme) gibi seçeneklerden birini yapmış olabilir.
    - created_at: Etkileşimin oluşturulma tarih ve saatini tutar. Bu, etkileşimin ne zaman yapıldığını gösterir.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=50, choices=[
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('view', 'View'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post', 'interaction_type')  # Aynı kullanıcı, aynı gönderiye aynı türde etkileşim yapamaz

    def save(self, *args, **kwargs):
        # Aynı kullanıcı ve aynı gönderiye var olan bir etkileşim türü varsa, güncellenir
        existing_interaction = UserInteraction.objects.filter(user=self.user, post=self.post, interaction_type=self.interaction_type).first()
        if existing_interaction:
            existing_interaction.created_at = self.created_at
            existing_interaction.save()
        else:
            super(UserInteraction, self).save(*args, **kwargs)
                       
class SharedPost(models.Model):
    """
    SharedPost modeli, bir kullanıcının başka bir kullanıcıya gönderi (post) paylaşmasını temsil eder.
    Bu modelde, gönderiyi paylaşan kullanıcı, paylaşılan kullanıcı, paylaşılan gönderi,
    eklenen bir mesaj ve paylaşımın oluşturulma tarihi gibi bilgiler bulunur.

    Alanlar:
    - sender: Gönderiyi paylaşan kullanıcı.
    - recipient: Gönderiyi alan kullanıcı.
    - post: Paylaşılan gönderi.
    - message: Gönderiyi paylaşırken eklenen isteğe bağlı mesaj.
    - created_at: Paylaşımın oluşturulma tarihi.
    
    Yöntemler:
    - clean: Kullanıcının bir gönderiyi kendisiyle paylaşmasını engeller.
    - __str__: Paylaşımı tanımlayan string temsili döndürür.
    """
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_posts")  # Gönderiyi paylaşan kullanıcı
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_posts")  # Gönderiyi alan kullanıcı
    post = models.ForeignKey('Post', on_delete=models.CASCADE)  # Paylaşılan gönderi
    message = models.TextField(blank=True, null=True)  # Paylaşırken eklenen mesaj (isteğe bağlı)
    created_at = models.DateTimeField(auto_now_add=True)  # Paylaşımın oluşturulma tarihi

    def clean(self):
        """
        Bu metod, kullanıcının bir gönderiyi kendisiyle paylaşmasını engeller.
        Eğer `sender` ve `recipient` aynı kullanıcıysa, bir hata fırlatılır.
        """
        if self.sender == self.recipient:
            raise ValidationError("A user cannot share a post with themselves.")
    
    def __str__(self):
        """
        Bu metod, paylaşımın string temsiline, gönderen kullanıcıyı ve alıcıyı içerir.
        Örneğin: "Shared Post from User1 to User2"
        """
        return f"Shared Post from {self.sender.username} to {self.recipient.username}"