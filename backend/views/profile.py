from rest_framework import generics, permissions
from backend.models import Profile
from backend.serializers import ProfileSerializer

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Giriş yapmış kullanıcının profilini döner."""
        return self.request.user.profile
