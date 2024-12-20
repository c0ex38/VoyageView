from rest_framework.generics import ListAPIView
from backend.models import Profile
from backend.serializers import ProfileSerializer

class ProminentUsersView(ListAPIView):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.annotate(total_followers=Count('followers')).order_by('-total_followers')[:10]
