from rest_framework import serializers
from django.contrib.auth.models import User
from backend.models import Follow, GroupInvitation, GroupChat, GroupMessage,SharedPost, Message, Report, Notification, User, Profile, Comment, Tag, PostMedia, Post

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class GroupInvitationSerializer(serializers.ModelSerializer):
    invited_user = UserSerializer(read_only=True)
    invited_by = UserSerializer(read_only=True)
    group = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GroupInvitation
        fields = ['id', 'group', 'invited_user', 'invited_by', 'created_at', 'is_accepted', 'is_rejected']
        read_only_fields = ['id', 'group', 'invited_user', 'invited_by', 'created_at']

class GroupChatSerializer(serializers.ModelSerializer):
    admins = UserSerializer(many=True, read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = GroupChat
        fields = ['id', 'name', 'members', 'admins', 'created_at']
        read_only_fields = ['id', 'admins', 'members', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        group = GroupChat.objects.create(**validated_data)
        group.members.add(user)  # Grup yaratıcısı otomatik üye olur.
        group.admins.add(user)  # Grup yaratıcısı otomatik yönetici olur.
        return group

class SharedPostSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField(write_only=True, required=True)
    recipient_id = serializers.IntegerField(write_only=True, required=True)
    post_title = serializers.CharField(source='post.title', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)

    class Meta:
        model = SharedPost
        fields = ['id', 'post_id', 'recipient_id', 'sender', 'post_title', 'recipient_username', 'message', 'created_at']
        read_only_fields = ['id', 'sender', 'post_title', 'recipient_username', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    recipient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    attachment = serializers.FileField(required=False)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'created_at', 'is_read', 'attachment']
        read_only_fields = ['id', 'sender', 'created_at', 'is_read']

    def validate_attachment(self, value):
        """Dosya türünü kontrol et"""
        if value:
            if not value.name.endswith(('.jpg', '.jpeg', '.png', '.mp4')):
                raise serializers.ValidationError("Invalid file type")
        return value

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

    def get_notification_details(self, obj):
        if obj.notification_type == 'like':
            return {"liked_post": obj.post.title}
        elif obj.notification_type == 'comment':
            return {"commented_post": obj.post.title}
        return {}

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
        if obj.level >= 500:
            return {"badge": "gold", "message": "Gold Badge - Influencer", "icon": "path_to_gold_icon.png"}
        elif obj.level >= 100:
            return {"badge": "silver", "message": "Silver Badge - Active User", "icon": "path_to_silver_icon.png"}
        elif obj.level >= 50:
            return {"badge": "bronze", "message": "Bronze Badge - Intermediate User", "icon": "path_to_bronze_icon.png"}
        else:
            return {"badge": "new", "message": "Welcome Badge - New User", "icon": "path_to_default_icon.png"}

    def get_profile_image(self, obj):
        """Profil resminin URL'sini döndürür, yoksa default resim döner."""
        if obj.profile_image:
            return obj.profile_image.url
        return "https://example.com/default_profile_image.png"

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    liked_by = UserSerializer(source='likes', many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'parent', 'likes_count', 'is_liked', 'liked_by', 'replies', 'created_at']
        read_only_fields = ['id', 'author', 'created_at', 'post']

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
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'category']

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
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'description', 'category', 'location_name', 'latitude', 'longitude', 'author',
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
        
        # Etiketleri işlemeye başla
        if tags_data:
            tags = [Tag.objects.get_or_create(name=tag.strip())[0] for tag in tags_data if tag.strip()]
            post.tags.add(*tags)
        
        # Medyaları ekle
        media_objects = []
        for media_file in media_data:
            media_type = 'video' if 'video' in media_file.content_type else 'image'
            media_objects.append(PostMedia(post=post, file=media_file, media_type=media_type))
        
        # Bulk create medya dosyalarını ekle
        if media_objects:
            PostMedia.objects.bulk_create(media_objects)

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
            tags = [Tag.objects.get_or_create(name=tag.strip())[0] for tag in tags_data if tag.strip()]
            instance.tags.add(*tags)
        
        # Medyaları güncelle
        if media_data:
            instance.media.all().delete()  # Eski medyaları sil
            media_objects = [
                PostMedia(post=instance, file=media_file, media_type='video' if 'video' in media_file.content_type else 'image')
                for media_file in media_data
            ]
            # Bulk create medya dosyalarını ekle
            PostMedia.objects.bulk_create(media_objects)
        
        return instance
