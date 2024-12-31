from rest_framework.generics import ListAPIView
from backend.models import Profile
from backend.serializers import ProfileSerializer
from django.db.models import Count

class ProminentUsersView(ListAPIView):
    """
    En fazla takipçiye sahip kullanıcıları listeleyen endpoint.
    - Kullanıcıların takipçi sayısına göre sıralama yapılır ve en fazla takipçiye sahip ilk 10 kullanıcı döndürülür.
    """
    serializer_class = ProfileSerializer

    def get_queryset(self):
        """
        Kullanıcıların toplam takipçi sayısını hesaplar ve en fazla takipçiye sahip 10 kullanıcıyı döndürür.
        """
        return Profile.objects.annotate(total_followers=Count('followers')).order_by('-total_followers')[:10]
