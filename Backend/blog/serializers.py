from rest_framework import serializers
from django.core.files.base import ContentFile
import base64
import json
from .models import BlogPost, Category, Comment, ReadingList
from django.utils.text import slugify


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'post_count']

    def get_post_count(self, obj):
        return obj.posts.filter(status='PUBLISHED', is_approved=True).count()


class BlogPostSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    author = serializers.SerializerMethodField()
    tags = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
        help_text="Virgülle ayrılmış etiketler veya JSON formatında etiket listesi"
    )
    tags_list = serializers.SerializerMethodField(read_only=True)
    read_time = serializers.SerializerMethodField()
    like_status = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    location_data = serializers.SerializerMethodField()
    popularity_score = serializers.SerializerMethodField()
    engagement_stats = serializers.SerializerMethodField()
    share_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            # Temel alanlar
            'id', 'title', 'slug', 'content', 'summary',
            
            # Kategori ve yazar bilgileri
            'category', 'category_id', 'author',
            
            # Etiketler
            'tags', 'tags_list',
            
            # Medya
            'cover_image', 'media_file',
            
            # Durum bilgileri
            'status', 'is_published', 'is_approved', 'is_featured',
            
            # İstatistikler
            'read_count', 'like_count', 'comment_count', 'read_time',
            'like_status', 'popularity_score', 'engagement_stats',
            
            # Konum bilgileri
            'location', 'location_data', 'latitude', 'longitude', 'location_details',
            
            # Zaman bilgileri
            'created_at', 'updated_at', 'published_at',
            
            # SEO
            'seo_title', 'seo_description', 'seo_keywords',
            
            # Paylaşım
            'share_url'
        ]
        read_only_fields = [
            'slug', 'created_at', 'updated_at', 'published_at',
            'read_count', 'like_count', 'popularity_score', 'engagement_stats',
            'share_url'
        ]

    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'full_name': f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username,
            'profile_picture': obj.author.profile_picture.url if obj.author.profile_picture else None
        }

    def validate_tags(self, value):
        if isinstance(value, str):
            try:
                tags = json.loads(value)
                if isinstance(tags, list):
                    return ','.join(tags)
            except json.JSONDecodeError:
                return value
        return value

    def get_tags_list(self, obj):
        return [tag.strip() for tag in obj.tags.split(',') if tag.strip()] if obj.tags else []

    def get_location_data(self, obj):
        location_data = {
            'location': obj.location,
            'latitude': float(obj.latitude) if obj.latitude else None,
            'longitude': float(obj.longitude) if obj.longitude else None,
            'details': obj.location_details or {},
            'formatted_address': None,
            'place_type': None
        }

        if obj.location_details:
            details = obj.location_details
            location_data.update({
                'formatted_address': f"{details.get('city', '')}, {details.get('country', '')}".strip(', '),
                'place_type': details.get('place_type', 'unknown')
            })

        return location_data

    def get_read_time(self, obj):
        words_per_minute = 200
        word_count = len(obj.content.split())
        minutes = word_count / words_per_minute
        return round(minutes)

    def get_like_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_popularity_score(self, obj):
        like_weight = 0.4
        read_weight = 0.3
        comment_weight = 0.2
        favorite_weight = 0.1

        score = (
            (obj.like_count * like_weight) +
            (obj.read_count * read_weight) +
            (obj.comments.count() * comment_weight) +
            (obj.favorites.count() * favorite_weight)
        )
        
        return round(score, 2)

    def get_engagement_stats(self, obj):
        return {
            'likes': obj.like_count,
            'reads': obj.read_count,
            'comments': obj.comments.count(),
            'favorites': obj.favorites.count()
        }

    def get_share_url(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(f'/post/{obj.slug}')
        return f'/post/{obj.slug}'

    def validate(self, data):
        if len(data.get('title', '')) < 5:
            raise serializers.ValidationError(
                {"title": "Başlık en az 5 karakter olmalıdır."}
            )
        
        if len(data.get('content', '')) < 100:
            raise serializers.ValidationError(
                {"content": "İçerik en az 100 karakter olmalıdır."}
            )

        if data.get('latitude') and (data['latitude'] < -90 or data['latitude'] > 90):
            raise serializers.ValidationError(
                {"latitude": "Enlem -90 ile 90 arasında olmalıdır."}
            )
            
        if data.get('longitude') and (data['longitude'] < -180 or data['longitude'] > 180):
            raise serializers.ValidationError(
                {"longitude": "Boylam -180 ile 180 arasında olmalıdır."}
            )

        return data


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    parent_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 
            'blog_post', 
            'user', 
            'content', 
            'created_at',
            'parent',
            'parent_user',
            'replies',
            'reply_count',
            'is_approved'
        ]
        read_only_fields = ['user', 'blog_post', 'created_at', 'parent_user']

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username,
            'profile_picture': obj.user.profile_picture.url if obj.user.profile_picture else None
        }

    def get_replies(self, obj):
        if hasattr(obj, 'replies') and obj.replies.exists():
            return CommentSerializer(
                obj.replies.all().order_by('created_at'), 
                many=True, 
                context={'parent_view': True}
            ).data
        return []

    def get_reply_count(self, obj):
        if hasattr(obj, 'replies'):
            return obj.replies.count()
        return 0

    def get_parent_user(self, obj):
        if hasattr(obj, 'parent') and obj.parent:
            return {
                'id': obj.parent.user.id,
                'username': obj.parent.user.username,
                'full_name': f"{obj.parent.user.first_name} {obj.parent.user.last_name}".strip() or obj.parent.user.username
            }
        return None

    def to_representation(self, instance):
        """
        Ana yorumlar için tüm alanları, alt yorumlar için sadece temel alanları göster
        """
        # Eğer bu bir alt yorum ve ana listede gösteriliyorsa, None döndür
        if instance.parent and not self.context.get('parent_view'):
            return None
            
        ret = super().to_representation(instance)
        if instance.parent:  # Alt yorum ise
            ret.pop('replies', None)
            ret.pop('reply_count', None)
        return ret


class ReadingListSerializer(serializers.ModelSerializer):
    blog_post = BlogPostSerializer(read_only=True)
    
    class Meta:
        model = ReadingList
        fields = ['id', 'user', 'blog_post', 'added_at']
        read_only_fields = ['user', 'added_at']