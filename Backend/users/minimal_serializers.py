from rest_framework import serializers
from .models import CustomUser

class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal kullanıcı bilgileri için serializer"""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'profile_picture'] 