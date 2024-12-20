from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Report, Notification, User, Profile, Comment, Tag, PostMedia, Post

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'user', 'report_type', 'reason', 'post', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
        
class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()  # Gönderen kullanıcı adını döner
    post = serializers.StringRelatedField()
    comment = serializers.StringRelatedField()

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'sender', 'post', 'comment', 'is_read', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    followers = UserSerializer(source='followers.all', many=True, read_only=True)
    following = UserSerializer(source='following.all', many=True, read_only=True)
    level_message = serializers.SerializerMethodField()
    level_badge = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'bio', 'location', 'birth_date', 'phone_number', 'profile_image',
            'gender', 'social_link', 'created_at', 'followers_count', 'following_count',
            'followers', 'following', 'level', 'points', 'level_message', 'level_badge',
        ]

    def get_followers_count(self, obj):
        """Toplam takipçi sayısını döner."""
        return obj.followers.count()

    def get_following_count(self, obj):
        """Toplam takip edilen sayısını döner."""
        return obj.following.count()

    def get_level_message(self, obj):
        """Kullanıcı seviyesine göre mesaj döner."""
        if obj.level >= 10:
            return "Influencer - Top Level User!"
        elif obj.level >= 5:
            return "Active User - Keep up the good work!"
        elif obj.level >= 3:
            return "Intermediate User - You're progressing well!"
        else:
            return "New User - Welcome to the platform!"

    def get_level_badge(self, obj):
        """Kullanıcı seviyesine göre rozet döner."""
        if obj.level >= 10:
            return {
                "badge": "gold",
                "message": "Gold Badge - Influencer",
                "icon": "https://example.com/badges/gold.png"
            }
        elif obj.level >= 5:
            return {
                "badge": "silver",
                "message": "Silver Badge - Active User",
                "icon": "https://example.com/badges/silver.png"
            }
        elif obj.level >= 3:
            return {
                "badge": "bronze",
                "message": "Bronze Badge - Intermediate User",
                "icon": "https://example.com/badges/bronze.png"
            }
        else:
            return {
                "badge": "new",
                "message": "Welcome Badge - New User",
                "icon": "https://example.com/badges/new.png"
            }

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    liked_by = UserSerializer(source='likes', many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'parent', 'likes_count', 'is_liked', 'liked_by', 'replies', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all().order_by('-created_at'), many=True).data
        return []

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'media_type', 'file', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    media = PostMediaSerializer(many=True, read_only=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    tags_info = serializers.SerializerMethodField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    liked_by = UserSerializer(source='likes', many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'description', 'category', 'location', 'author',
            'tags', 'tags_info', 'media', 'comments', 'likes_count', 'is_liked', 'liked_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'likes_count', 'is_liked', 'liked_by', 'created_at', 'updated_at']

    def get_tags_info(self, obj):
        """Her bir tag için ayrı bir dictionary döndürür"""
        return [{'id': tag.id, 'name': tag.name} for tag in obj.tags.all()]

    def get_likes_count(self, obj):
        """Beğeni sayısını döndürür"""
        return obj.likes.count()

    def get_is_liked(self, obj):
        """Mevcut kullanıcının postu beğenip beğenmediğini döndürür"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        media_data = self.context.get('request').FILES.getlist('media', [])
        
        # Post oluşturma
        validated_data['author'] = self.context['request'].user
        post = Post.objects.create(**validated_data)
        
        # Her tag'i ayrı ayrı işle
        for tag_name in tags_data:
            # Strip kullanarak baştaki ve sondaki boşlukları temizle
            tag_name = tag_name.strip()
            # Köşeli parantezleri ve diğer işaretleri temizle
            tag_name = tag_name.strip('[]"\'')
            if tag_name:  # Boş string değilse
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)
        
        # Medyaları ekle
        for media_file in media_data:
            media_type = 'video' if 'video' in media_file.content_type else 'image'
            PostMedia.objects.create(
                post=post,
                file=media_file,
                media_type=media_type
            )
        
        return post

    def update(self, instance, validated_data):
        media_data = self.context.get('request').FILES.getlist('media', [])
        tags_data = validated_data.pop('tags', None)
        
        # Temel alanları güncelle
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Etiketleri güncelle
        if tags_data is not None:
            instance.tags.clear()
            for tag_name in tags_data:
                tag_name = tag_name.strip()
                tag_name = tag_name.strip('[]"\'')
                if tag_name:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    instance.tags.add(tag)
        
        # Medyaları güncelle
        if media_data:
            instance.media.all().delete()  # Eski medyaları sil
            for media_file in media_data:
                media_type = 'video' if 'video' in media_file.content_type else 'image'
                PostMedia.objects.create(
                    post=instance,
                    file=media_file,
                    media_type=media_type
                )
        
        return instance