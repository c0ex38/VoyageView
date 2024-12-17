from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'phone_number', 'profile_image', 'gender', 'social_link', 'created_at']
