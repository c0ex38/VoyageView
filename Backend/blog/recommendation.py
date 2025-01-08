"""
Blog yazıları için öneri sistemi
"""
from django.db.models import Count, F, Q
from django.db import models
from django.contrib.auth import get_user_model
from .models import BlogPost, ReadingList, Like, Favorite

User = get_user_model()

def recommend_posts(user_id, limit=10):
    """
    Kullanıcıya özel blog yazısı önerileri üretir.
    
    Öneriler şu kriterlere göre hesaplanır:
    1. Kullanıcının okuduğu yazıların kategorileri
    2. Kullanıcının beğendiği yazıların benzer etiketleri
    3. Kullanıcının okuma listesindeki yazıların özellikleri
    4. Kullanıcının favori yazılarının özellikleri
    
    Args:
        user_id (int): Öneriler üretilecek kullanıcının ID'si
        limit (int): Döndürülecek öneri sayısı
        
    Returns:
        list: Önerilen blog yazılarının ID listesi
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Kullanıcının etkileşimde bulunduğu yazılar
        read_posts = ReadingList.objects.filter(user=user).values_list('post_id', flat=True)
        liked_posts = Like.objects.filter(user=user).values_list('post_id', flat=True)
        favorite_posts = Favorite.objects.filter(user=user).values_list('post_id', flat=True)
        
        # Kullanıcının ilgilendiği kategoriler
        interested_categories = BlogPost.objects.filter(
            id__in=list(read_posts) + list(liked_posts) + list(favorite_posts)
        ).values_list('category_id', flat=True).distinct()
        
        # Kullanıcının ilgilendiği etiketler
        interested_tags = BlogPost.objects.filter(
            id__in=list(read_posts) + list(liked_posts) + list(favorite_posts)
        ).values_list('tags', flat=True)
        
        tag_list = []
        for tags in interested_tags:
            if tags:
                tag_list.extend([tag.strip() for tag in tags.split(',')])
        
        # Önerilen yazıları hesapla
        recommended_posts = BlogPost.objects.filter(
            Q(category_id__in=interested_categories) |
            Q(tags__icontains=','.join(tag_list[:5])) if tag_list else Q()
        ).exclude(
            # Kullanıcının zaten etkileşimde bulunduğu yazıları çıkar
            id__in=list(read_posts) + list(liked_posts) + list(favorite_posts)
        ).filter(
            # Sadece yayınlanmış ve onaylanmış yazıları göster
            is_published=True,
            is_approved=True
        ).annotate(
            # Popülerlik skorunu hesapla
            popularity_score=models.ExpressionWrapper(
                F('like_count') * 0.7 + F('read_count') * 0.3,
                output_field=models.FloatField()
            )
        ).order_by('-popularity_score')[:limit]
        
        return list(recommended_posts.values_list('id', flat=True))
        
    except User.DoesNotExist:
        return []
    except Exception as e:
        print(f"Öneri sistemi hatası: {str(e)}")
        return [] 