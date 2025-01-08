from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *

class Tag(models.Model):
    """
    Tag modeli, bir gönderiyi kategorize etmek veya etiketlemek için kullanılan etiketlerin adlarını tutar.
    
    Alanlar:
    - name: Etiketin adıdır. Her etiket benzersiz olmalıdır.
    
    Yöntemler:
    - __str__: Etiketin adını döndürür. Bu, etiket nesnesi yazdırıldığında daha anlamlı bir çıktı sağlar.
    """
    name = models.CharField(max_length=50, unique=True)  # Etiket adı, maksimum 50 karakter uzunluğunda ve benzersiz

    def __str__(self):
        """
        Etiketin adını döndürür. Bu, etiket nesnesi yazdırıldığında veya veri tabanında göründüğünde, etiketin adı gösterilir.
        """
        return self.name