from rest_framework import serializers
from django.db import models
from .models import CustomUser
from blog.models import BlogPost
from blog.serializers import BlogPostSerializer

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    profile_picture = serializers.ImageField(required=True)
    
    class Meta:
        model = CustomUser
        fields = (
            'username', 
            'email', 
            'password', 
            'confirm_password',
            'full_name',
            'date_of_birth',
            'profile_picture',
            'location',
            'latitude',
            'longitude'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'full_name': {'required': True},
            'date_of_birth': {'required': True},
            'location': {'required': True},
            'latitude': {'required': True},
            'longitude': {'required': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Şifreler eşleşmiyor!")
        
        # Varsayılan değerleri ekle
        if 'latitude' not in data:
            data['latitude'] = 0.0
        if 'longitude' not in data:
            data['longitude'] = 0.0
        if 'location' not in data:
            data['location'] = 'Konum belirtilmedi'
            
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        # Varsayılan değerleri kontrol et
        validated_data.setdefault('latitude', 0.0)
        validated_data.setdefault('longitude', 0.0)
        validated_data.setdefault('location', 'Konum belirtilmedi')
        
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'full_name', 'date_of_birth', 'profile_picture']
        read_only_fields = ['username']  # Kullanıcı adını değiştirmeye izin vermiyoruz


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'followers', 'following']


class UserProfileSerializer(serializers.ModelSerializer):
    total_followers = serializers.SerializerMethodField()
    total_following = serializers.SerializerMethodField()
    total_posts = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    recent_posts = serializers.SerializerMethodField()
    profile_completion = serializers.SerializerMethodField()
    join_date = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'full_name',
            'profile_picture',
            'date_of_birth',
            'location',
            'latitude',
            'longitude',
            'total_followers',
            'total_following',
            'total_posts',
            'total_likes',
            'is_following',
            'recent_posts',
            'profile_completion',
            'join_date',
            'is_email_verified'
        ]
        read_only_fields = ['email', 'is_email_verified']

    def get_total_followers(self, obj):
        return obj.followers.count()

    def get_total_following(self, obj):
        return obj.following.count()

    def get_total_posts(self, obj):
        return BlogPost.objects.filter(author=obj, is_published=True).count()

    def get_total_likes(self, obj):
        return BlogPost.objects.filter(author=obj).aggregate(
            total_likes=models.Sum('like_count')
        )['total_likes'] or 0

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.following.filter(id=obj.id).exists()
        return False

    def get_recent_posts(self, obj):
        recent_posts = BlogPost.objects.filter(
            author=obj,
            is_published=True
        ).order_by('-created_at')[:3]
        return BlogPostSerializer(recent_posts, many=True).data

    def get_profile_completion(self, obj):
        fields = {
            'full_name': 15,
            'profile_picture': 15,
            'date_of_birth': 10,
            'location': 10,
            'email': 10,
            'is_email_verified': 20,
            'latitude': 10,
            'longitude': 10
        }
        
        completion = 0
        for field, value in fields.items():
            if getattr(obj, field):
                completion += value
        
        return completion

    def get_join_date(self, obj):
        return obj.date_joined.strftime("%B %Y")  # Örnek: "Mart 2024"


class UserSettingsSerializer(serializers.ModelSerializer):
    """Kullanıcı ayarları için serializer"""
    class Meta:
        model = CustomUser
        fields = [
            'email',
            'full_name',
            'date_of_birth',
            'profile_picture',
            'location',
            'latitude',
            'longitude'
        ]
        extra_kwargs = {
            'email': {'read_only': True}
        }