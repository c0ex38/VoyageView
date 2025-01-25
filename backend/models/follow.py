from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *

class Follow(models.Model):
    """
    Follow modeli, bir kullanıcının başka bir kullanıcıyı takip etmesini temsil eder.
    Bu modelde, takip eden kullanıcı, takip edilen kullanıcı ve takip oluşturulma zamanı saklanır.
    
    Alanlar:
    - user: Takip eden kullanıcı. Bu kullanıcı, başka bir kullanıcıyı takip eder.
    - followed_user: Takip edilen kullanıcı. Bu kullanıcıyı takip eden kullanıcı izler.
    - created_at: Takip etme işleminin oluşturulma tarihi. Bu tarih, takip işleminin ne zaman başladığını belirtir.
    
    Yöntemler:
    - __str__: Takip işleminin string temsili döndürülür. Bu, takip eden kullanıcıyı ve takip edilen kullanıcıyı içerir.
    """
    
    user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)  # Takip eden kullanıcı
    followed_user = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)  # Takip edilen kullanıcı
    created_at = models.DateTimeField(auto_now_add=True)  # Takip etme işleminin oluşturulma tarihi

    class Meta:
        """
        Aynı kullanıcının aynı kişiyi takip etmesine izin verilmez.
        """
        unique_together = ('user', 'followed_user')  # Bir kullanıcı, aynı kişiyi birden fazla takip edemez

    def __str__(self):
        """
        Bu metod, takip eden kullanıcı ve takip edilen kullanıcıyı içeren bir string temsili döndürür.
        Örneğin: "User1 follows User2"
        """
        return f"{self.user.username} follows {self.followed_user.username}"