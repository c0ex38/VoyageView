from rest_framework import serializers
from .models import Profile, Post, Comment, Tag
from django.contrib.auth.models import User

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

    class Meta:
        model = Profile
        fields = [
            'bio', 'location', 'birth_date', 'phone_number', 'profile_image',
            'gender', 'social_link', 'created_at', 'followers_count', 'following_count', 'followers', 'following'
        ]

    def get_followers_count(self, obj):
        """Toplam takipçi sayısını döner."""
        return obj.followers.count()

    def get_following_count(self, obj):
        """Toplam takip edilen sayısını döner."""
        return obj.following.count()



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


class PostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)  # Görsel zorunlu
    category = serializers.CharField(required=True)  # Kategori zorunlu
    location = serializers.CharField(required=True)  # Konum zorunlu
    title = serializers.CharField(required=True)  # Başlık zorunlu
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()  # Beğeni sayısı
    is_liked = serializers.SerializerMethodField()  # Kullanıcı beğenmiş mi?
    liked_by = UserSerializer(source='likes', many=True, read_only=True)  # Beğenen kullanıcılar
    tags = TagSerializer(many=True, required=False)  # Etiketleri serializer ile göster


    class Meta:
        model = Post
        fields = [
            'id', 'title', 'description', 'image', 'category', 'location',
            'author', 'comments', 'likes_count', 'is_liked', 'tags', 'liked_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_likes_count(self, obj):
        """Toplam beğeni sayısını döner."""
        return obj.likes.count()

    def get_is_liked(self, obj):
        """Kullanıcının bu post'u beğenip beğenmediğini kontrol eder."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_data['name'])
            post.tags.add(tag)
        return post

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        instance = super().update(instance, validated_data)
        if tags_data:
            instance.tags.clear()
            for tag_data in tags_data:
                tag, created = Tag.objects.get_or_create(name=tag_data['name'])
                instance.tags.add(tag)
        return instance
