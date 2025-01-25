from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils.timezone import now
from backend.utils.validators import *
from .group_chat import GroupChat

class GroupInvitation(models.Model):
    """
    GroupInvitation modeli, bir kullanıcıyı grup sohbetine davet etmeyi temsil eder. 
    Bu model, davetin alıcısını, göndereni, davetin kabul veya reddedilme durumunu 
    ve davetin oluşturulma zamanını tutar.

    Alanlar:
    - group: Davetin ait olduğu grup sohbeti. Bir grup sohbetine birden fazla davet yapılabilir.
    - invited_user: Davet edilen kullanıcı. Bu, gruba katılması için davet edilen kişiyi belirtir.
    - invited_by: Daveti gönderen kullanıcı. Bu, davetiyeyi gönderen kişiyi belirtir.
    - created_at: Davetin oluşturulma tarihi.
    - is_accepted: Davet kabul edildi mi? Varsayılan olarak 'False' (kabul edilmedi).
    - is_rejected: Davet reddedildi mi? Varsayılan olarak 'False' (reddedilmedi).
    
    Yöntemler:
    - __str__: Davet edilen kullanıcıyı ve grup adını içeren bir string temsili döndürür.
    - clean: Davetin hem kabul edilip hem reddedilemeyeceğini kontrol eder ve buna göre hata fırlatır.
    """
    
    group = models.ForeignKey(GroupChat, related_name="invitations", on_delete=models.CASCADE)  # Davetin ait olduğu grup
    invited_user = models.ForeignKey(User, related_name="group_invitations", on_delete=models.CASCADE)  # Davet edilen kullanıcı
    invited_by = models.ForeignKey(User, related_name="sent_invitations", on_delete=models.CASCADE)  # Daveti gönderen kullanıcı
    created_at = models.DateTimeField(auto_now_add=True)  # Davetin oluşturulma tarihi
    is_accepted = models.BooleanField(default=False)  # Davet kabul edildi mi?
    is_rejected = models.BooleanField(default=False)  # Davet reddedildi mi?

    def clean(self):
        """
        Bu metod, bir davetin aynı anda hem kabul edilip hem reddedilmemesi gerektiğini kontrol eder.
        Eğer bu durum söz konusuysa, bir ValidationError fırlatılır.
        """
        if self.is_accepted and self.is_rejected:
            raise ValidationError("A group invitation cannot be both accepted and rejected at the same time.")
    
    def __str__(self):
        """
        Bu metod, davet edilen kullanıcıyı ve davetin ait olduğu grubu içeren bir string temsili döndürür.
        Örneğin: "Invitation to UserName for GroupChatName"
        """
        return f"Invitation to {self.invited_user.username} for {self.group.name}"