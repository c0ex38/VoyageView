# Django Rest Framework İlgili Kütüphaneler
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter, BaseFilterBackend
import openai
from django.conf import settings
import google.generativeai as genai
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
import json
from rest_framework.exceptions import PermissionDenied
from PIL import Image
import io
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.functions import Greatest
from django.contrib.postgres.search import TrigramSimilarity

# Filtreleme Kütüphaneleri
from django_filters.rest_framework import DjangoFilterBackend

from users.models import CustomUser
# Uygulama Modelleri
from .models import BlogPost, Category, Like, Comment, Favorite, ReadingList
from django.db.models import F, FloatField, ExpressionWrapper, Q, Func
from django.db import models
from django.db.models.functions import Radians, Sin, Cos, ACos

# Uygulama Serializer'ları
from .serializers import (
    BlogPostSerializer,
    CategorySerializer,
    CommentSerializer,
    ReadingListSerializer,
)

# Uygulama İçindeki Diğer Yardımcı Modüller
from .recommendation import recommend_posts
from .permissions import IsOwnerOrReadOnly
from .filters import BlogPostFilter
from notifications.utils import create_notification
from .pagination import CustomPagination

User = get_user_model()

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    İki nokta arasındaki mesafeyi hesaplar (Haversine formülü)
    """
    R = 6371  # Dünya'nın yarıçapı (km)

    lat1_rad = Radians(lat1)
    lon1_rad = Radians(lon1)
    lat2_rad = Radians(lat2)
    lon2_rad = Radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = Sin(dlat/2)**2 + Cos(lat1_rad) * Cos(lat2_rad) * Sin(dlon/2)**2
    c = 2 * ACos(Func(a**0.5))
    distance = R * c

    return ExpressionWrapper(distance, output_field=FloatField())

class BlogPostListCreateView(generics.ListCreateAPIView):
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        queryset = BlogPost.objects.all()
        
        # Yetkilendirme kontrolü
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(author=self.request.user) |
                Q(status='PUBLISHED', is_approved=True)
            )
            
        # Konum bazlı filtreleme
        latitude = self.request.query_params.get('lat')
        longitude = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius', 10)  # km cinsinden
        
        if latitude and longitude:
            try:
                lat = float(latitude)
                lng = float(longitude)
                radius_km = float(radius)
                
                queryset = queryset.annotate(
                    distance=calculate_distance(
                        lat, lng,
                        F('latitude'), F('longitude')
                    )
                ).filter(distance__lte=radius_km).order_by('distance')
                
            except (ValueError, TypeError):
                pass
            
        return queryset

    def generate_from_image(self, image_file):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            image = Image.open(image_file)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format or 'JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            prompt = """
            Sen profesyonel bir Türk blog yazarısın. Bu görsele bakarak yanıt ver.
            ÖNEMLI: Yanıtınını sadece JSON formatında ver, başka bir şey ekleme.
            
            1. Etkileyici bir Türkçe başlık öner
            2. 3-4 paragraflık bir Türkçe blog yazısı oluştur
            3. 2-3 cümlelik Türkçe özet yaz
            4. SEO için Türkçe anahtar kelimeler öner (en az 5 kelime)
            5. En uygun kategoriyi seç: TRAVEL, FOOD, CULTURE, ADVENTURE veya OTHER
            6. Görseldeki konumu tahmin et ve koordinatlarını bul
            
            SADECE şu formatta yanıt ver:
            {
                "title": "Önerilen Başlık",
                "content": "Blog içeriği...",
                "summary": "Kısa özet...",
                "keywords": ["kelime1", "kelime2", "kelime3", "kelime4", "kelime5"],
                "category": "TRAVEL",
                "location": {
                    "name": "Konum adı",
                    "city": "Şehir",
                    "country": "Ülke",
                    "latitude": 41.0082,
                    "longitude": 28.9784
                }
            }
            """

            response = model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": img_byte_arr}
            ])
            
            if not response.text:
                return None
                
            ai_response = json.loads(response.text.strip())
            
            # Keywords'ü liste formatına çevir
            if isinstance(ai_response.get('keywords'), str):
                ai_response['keywords'] = [k.strip() for k in ai_response['keywords'].split(',')]
            
            return ai_response
                    
        except Exception as e:
            print(f"Görsel analizi hatası: {str(e)}")
            return None

    def post(self, request, *args, **kwargs):
        try:
            # Görsel analizi
            if 'analyze_image' in request.data and request.FILES.get('cover_image'):
                ai_response = self.generate_from_image(request.FILES['cover_image'])
                if not ai_response:
                    return Response({
                        'status': 'error',
                        'message': 'Görsel analizi başarısız oldu'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Kategori ID'sini bul
                category_name = ai_response.get('category', 'OTHER')
                try:
                    category = Category.objects.get(name=category_name)
                except Category.DoesNotExist:
                    category = Category.objects.get(name='OTHER')

                return Response({
                    'status': 'success',
                    'message': 'Görsel analizi başarılı',
                    'data': {
                        'title': ai_response.get('title'),
                        'content': ai_response.get('content'),
                        'summary': ai_response.get('summary'),
                        'keywords': ai_response.get('keywords'),
                        'category_id': category.id,
                        'suggested_category': category_name,
                        'location': ai_response.get('location', {})
                    }
                })

            # Normal post işlemi
            return self.create(request, *args, **kwargs)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Etiketleri işle
        tags = self.request.data.get('tags', [])
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except json.JSONDecodeError:
                tags = [tag.strip() for tag in tags.split(',')]
        
        tags_str = ','.join(tags) if isinstance(tags, list) else str(tags)

        # Location detaylarını işle
        location_details = self.request.data.get('location_details', {})
        if isinstance(location_details, str):
            try:
                location_details = json.loads(location_details)
            except json.JSONDecodeError:
                location_details = {}

        try:
            instance = serializer.save(
                author=self.request.user,
                status='PENDING',
                tags=tags_str,
                location_details=location_details
            )

            # Dosyayı kaydet
            if 'cover_image' in self.request.FILES:
                instance.cover_image = self.request.FILES['cover_image']
                instance.save()

        except Exception as e:
            raise serializers.ValidationError({
                'error': str(e),
                'detail': 'Post oluşturulurken bir hata oluştu'
            })

    def generate_summary(self, content, title):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            prompt = f"""
            Sen profesyonel bir blog editörüsün. Aşağıdaki blog yazısı için JSON formatında yanıt ver.
            
            Başlık: {title}
            İçerik: {content}
            
            Yanıtını şu formatta ver:
            {{
                "summary": "2-3 cümlelik etkileyici bir özet",
                "keywords": ["anahtar", "kelimeler", "listesi"],
                "category": "TRAVEL, FOOD, CULTURE, ADVENTURE veya OTHER kategorilerinden biri"
            }}
            """
            
            response = model.generate_content(prompt)
            if not response.text:
                return None
                
            ai_response = json.loads(response.text.strip())
            
            # Yanıt formatını doğrula
            required_keys = ['summary', 'keywords', 'category']
            if not all(key in ai_response for key in required_keys):
                return None

            # Kategoriyi doğrula
            valid_categories = ['TRAVEL', 'FOOD', 'CULTURE', 'ADVENTURE', 'OTHER']
            if ai_response['category'] not in valid_categories:
                ai_response['category'] = 'OTHER'
                
            # Keywords'ü string'e çevir
            if isinstance(ai_response['keywords'], list):
                ai_response['keywords'] = ', '.join(ai_response['keywords'])
                
            return ai_response
                
        except Exception as e:
            print(f"Gemini AI error: {e}")
            return None

    def get_user_id(self):
        if isinstance(self.request.user, CustomUser):
            return self.request.user.id
        return None

class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Görüntülenme sayısını artır
        if request.user != self.get_object().author:
            self.get_object().view_count = F('view_count') + 1
            self.get_object().save()
        return response

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.author and not self.request.user.is_staff:
            raise PermissionDenied("Bu yazıyı düzenleme yetkiniz yok.")
            
        # İçerik değiştiyse yeni özet oluştur
        if 'content' in self.request.data:
            ai_response = BlogPostListCreateView.generate_summary(
                self, 
                self.request.data['content'],
                self.request.data.get('title', serializer.instance.title)
            )
            if ai_response:
                serializer.save(
                    summary=ai_response['summary'],
                    seo_keywords=ai_response['keywords'],
                    suggested_category=ai_response['category']
                )
            else:
                serializer.save()
        else:
            serializer.save()
       
class AISearchFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        ai_search = request.query_params.get('ai_search')
        if not ai_search:
            return queryset

        try:
            # Gemini AI'yı yapılandır
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')

            # AI'dan arama terimleri al
            prompt = f"""
            Bu arama sorgusunu blog aramak için kullanılacak anahtar kelimelere dönüştür:
            Sorgu: "{ai_search}"
            
            Lütfen sadece virgülle ayrılmış anahtar kelimeleri döndür.
            Örnek yanıt formatı: "kelime1, kelime2, kelime3"
            """

            response = model.generate_content(prompt)
            if response.text:
                # AI'dan gelen kelimeleri temizle ve liste haline getir
                keywords = [word.strip() for word in response.text.replace('"', '').split(',')]
                
                # Her bir anahtar kelime için Q nesnesi oluştur
                q_objects = Q()
                for keyword in keywords:
                    q_objects |= (
                        Q(title__icontains=keyword) |
                        Q(content__icontains=keyword) |
                        Q(summary__icontains=keyword) |
                        Q(tags__icontains=keyword) |
                        Q(location__icontains=keyword)
                    )
                
                return queryset.filter(q_objects).distinct()

        except Exception as e:
            print(f"AI arama hatası: {str(e)}")
            
        return queryset

class BlogPostSearchFilterView(ListAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    filter_backends = [AISearchFilter, DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BlogPostFilter
    search_fields = ['title', 'content', 'summary', 'tags', 'location']
    ordering_fields = ['like_count', 'created_at', 'updated_at']
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(status='PUBLISHED')
        
        # Konum bazlı filtreleme
        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        distance = float(self.request.query_params.get('distance', 10))  # varsayılan 10km
        
        if latitude and longitude:
            try:
                lat = float(latitude)
                lon = float(longitude)
                
                # Haversine formülü ile mesafe hesaplama
                queryset = queryset.annotate(
                    distance=ExpressionWrapper(
                        6371 * ACos(
                            Cos(Radians(lat)) * 
                            Cos(Radians(F('latitude'))) * 
                            Cos(Radians(F('longitude')) - Radians(lon)) + 
                            Sin(Radians(lat)) * 
                            Sin(Radians(F('latitude')))
                        ),
                        output_field=FloatField()
                    )
                ).filter(distance__lte=distance)
            except ValueError:
                pass
        
        return queryset

class PublishedBlogPostsView(generics.ListAPIView):
    serializer_class = BlogPostSerializer

    def get_queryset(self):
        return BlogPost.objects.filter(is_approved=True, is_published=True)

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
class LikeBlogPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, blog_post_id):
        try:
            blog_post = BlogPost.objects.get(id=blog_post_id)
            like, created = Like.objects.get_or_create(user=request.user, blog_post=blog_post)

            if created:
                blog_post.like_count += 1
                blog_post.save()
                create_notification(blog_post.author, f"{request.user.username} liked your post '{blog_post.title}'.")
                return Response({'message': 'Blog post liked successfully.'}, status=status.HTTP_201_CREATED)
            else:
                like.delete()
                blog_post.like_count -= 1
                blog_post.save()
                return Response({'message': 'Blog post unliked successfully.'}, status=status.HTTP_200_OK)

        except BlogPost.DoesNotExist:
            return Response({'message': 'Blog post not found.'}, status=status.HTTP_404_NOT_FOUND)

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        blog_post_id = self.kwargs.get('blog_post_id')
        return Comment.objects.filter(blog_post_id=blog_post_id)

    def perform_create(self, serializer):
        blog_post_id = self.kwargs.get('blog_post_id')
        blog_post = BlogPost.objects.get(id=blog_post_id)
        serializer.save(user=self.request.user, blog_post=blog_post)
        create_notification(blog_post.author, f"{self.request.user.username} commented on your post '{blog_post.title}'.")

class CommentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
   
class ModerationCommentListView(ListAPIView):
    queryset = Comment.objects.filter(is_approved=False)
    serializer_class = CommentSerializer
    permission_classes = [IsAdminUser]

class ApproveCommentView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            comment.is_approved = True
            comment.save()
            return Response({"message": "Comment approved successfully."}, status=200)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=404)     
  
class FavoriteBlogPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, blog_post_id):
        try:
            blog_post = BlogPost.objects.get(id=blog_post_id)
            favorite, created = Favorite.objects.get_or_create(user=request.user, blog_post=blog_post)

            if created:
                return Response({'message': 'Blog post added to favorites.'}, status=status.HTTP_201_CREATED)
            else:
                favorite.delete()
                return Response({'message': 'Blog post removed from favorites.'}, status=status.HTTP_200_OK)

        except BlogPost.DoesNotExist:
            return Response({'message': 'Blog post not found.'}, status=status.HTTP_404_NOT_FOUND)
               
class PopularBlogPostsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BlogPostSerializer

    def get_queryset(self):
        """
        Blog yazılarını popülerlik skoruna göre sıralar.
        Popülerlik Skoru = (like_count * 0.7) + (read_count * 0.3)
        """
        return BlogPost.objects.filter(is_approved=True, is_published=True).annotate(
            popularity_score=ExpressionWrapper(
                F('like_count') * 0.7 + F('read_count') * 0.3, output_field=FloatField()
            )
        ).order_by('-popularity_score')

class MLPersonalizedPopularBlogPostsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            # Sayfalama parametrelerini al
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            user = request.user
            # Yapay zeka destekli öneri fonksiyonu
            recommended_posts = recommend_posts(user)

            if recommended_posts.empty:
                return Response({
                    "message": "Öneri bulunamadı.",
                    "results": [],
                    "count": 0,
                    "total_pages": 0,
                    "current_page": page,
                    "links": {
                        "next": None,
                        "previous": None
                    }
                }, status=200)

            # BlogPost modellerini al
            post_ids = recommended_posts["id"].tolist()
            posts = BlogPost.objects.filter(
                id__in=post_ids,
                is_published=True,
                is_approved=True
            ).select_related(
                'author',
                'category'
            ).prefetch_related(
                'comments',
                'favorites'
            )

            # Sayfalama
            paginator = Paginator(list(posts), page_size)
            paginated_posts = paginator.get_page(page)

            # Serializer ile döndür
            serializer = BlogPostSerializer(
                paginated_posts, 
                many=True, 
                context={'request': request}
            )

            # Önerilen yazıların sıralaması
            sorted_posts = sorted(
                serializer.data,
                key=lambda x: post_ids.index(x["id"])
            )

            # Sayfalama bilgilerini ekle
            next_page = page + 1 if page < paginator.num_pages else None
            previous_page = page - 1 if page > 1 else None

            return Response({
                "results": sorted_posts,
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page,
                "links": {
                    "next": f"?page={next_page}&page_size={page_size}" if next_page else None,
                    "previous": f"?page={previous_page}&page_size={page_size}" if previous_page else None
                }
            }, status=200)

        except Exception as e:
            print(f"ML Personalized Posts Error: {str(e)}")
            return Response({
                "message": "Öneriler alınırken bir hata oluştu.",
                "error": str(e)
            }, status=500)

class AddToReadingListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, blog_post_id):
        blog_post = BlogPost.objects.get(id=blog_post_id)
        reading_list, created = ReadingList.objects.get_or_create(user=request.user, blog_post=blog_post)
        if created:
            return Response({"message": "Added to reading list."}, status=201)
        return Response({"message": "Already in reading list."}, status=200)

class ReadingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reading_list = ReadingList.objects.filter(user=request.user)
        serializer = ReadingListSerializer(reading_list, many=True)
        return Response(serializer.data, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_summary(request):
    content = request.data.get('content', '')
    title = request.data.get('title', '')
    
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Sen profesyonel bir blog yazarısın. Aşağıdaki blog yazısı için çok kısa ve etkileyici bir özet yazman gerekiyor.

        Başlık: {title}
        İçerik: {content}

        Önemli Kurallar:
        1. Özet maksimum 100 karakter olmalı
        2. Yazının ana fikrini tek cümlede aktarmalı
        3. İlgi çekici ve merak uyandırıcı olmalı
        4. Teknik detaylardan kaçınmalı
        5. Nokta ile bitmelidir.

        Lütfen sadece özeti yaz, başka bir şey ekleme.
        """
        
        response = model.generate_content(prompt)
        
        if response.text:
            summary = response.text.strip()
            # Eğer özet 100 karakterden uzunsa kısalt
            if len(summary) > 100:
                summary = summary[:97] + "..."
            return Response({'summary': summary})
            
        return Response({'error': 'Özet oluşturulamadı'}, status=400)
            
    except Exception as e:
        print(f"Gemini AI error: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_location(request):
    location = request.data.get('location', '')
    content = request.data.get('content', '')
    
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Sen bir seyahat uzmanısın. Aşağıdaki konum ve blog içeriğini analiz ederek, 
        seyahat edecek kişiler için faydalı bilgiler çıkar.

        Konum: {location}
        Blog İçeriği: {content}

        Lütfen aşağıdaki formatta yanıt ver:
        {{
            "best_time_to_visit": "En iyi ziyaret zamanı",
            "must_see_places": ["Mutlaka görülmesi gereken 3 yer"],
            "local_tips": ["Yerel 3 önemli ipucu"],
            "weather_info": "Hava durumu özeti",
            "transportation": "Ulaşım tavsiyeleri",
            "estimated_budget": "Tahmini günlük bütçe (USD)"
        }}
        """
        
        response = model.generate_content(prompt)
        
        if response.text:
            return Response(eval(response.text.strip()))
        return Response({'error': 'Konum analizi yapılamadı'}, status=400)
            
    except Exception as e:
        print(f"Location analysis error: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@parser_classes([MultiPartParser])
def analyze_media(request):
    media_file = request.FILES.get('media_file')
    if not media_file:
        return Response({'error': 'No media file provided'}, status=400)
    
    try:
        # Gemini AI yapılandırması
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Medya dosyasını analiz et
        response = model.generate_content([
            "Bu görseli/videoyu analiz et ve bir blog yazısı için şunları öner:",
            media_file
        ])
        
        # AI önerilerini oluştur
        suggestions = {
            "title": "Önerilen başlık buraya gelecek",
            "content": "Önerilen içerik buraya gelecek",
            "tags": "önerilen, etiketler, buraya, gelecek",
            "category_suggestion": "Önerilen kategori"
        }
        
        return Response(suggestions)
            
    except Exception as e:
        print(f"Media analysis error: {e}")
        return Response({'error': str(e)}, status=500)

class PopularPostsView(generics.ListAPIView):
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    
    def get_queryset(self):
        return BlogPost.objects.filter(
            is_published=True
        ).order_by('-view_count', '-created_at')[:10]

class ImageAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.FILES.get('image'):
            return Response({
                'status': 'error',
                'message': 'Lütfen bir görsel yükleyin'
            }, status=status.HTTP_400_BAD_REQUEST)

        return self.generate_from_image(request.FILES['image'])

    def generate_from_image(self, image_file):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            image = Image.open(image_file)
            
            prompt = """
            Sen lokasyon tabanlı bir sosyal medya platformunda çalışan profesyonel içerik analistsin.
            Bu fotoğraf bir kullanıcı tarafından belirli bir konumda çekilmiş ve paylaşılmak isteniyor.

            Görseli detaylıca analiz et ve şu bilgilere özellikle dikkat et:
            1. Fotoğrafın nerede çekilmiş olabileceği (spesifik konum)
            2. Kullanıcının bu konumu neden seçmiş olabileceği
            3. Bu konumun etrafındaki ilgi çekici noktalar
            4. Ziyaretçiler için en iyi fotoğraf çekim noktaları
            5. Konumun en iyi ziyaret zamanı ve önemli ipuçları

            Yanıtını tam olarak şu JSON formatında ver, başka bir şey ekleme:
            {
                "title": "Kullanıcının paylaşımı için etkileyici bir Türkçe başlık",
                "content": "3-4 paragraflık bir Türkçe blog yazısı. İlk paragraf konumun genel tanımı, ikinci paragraf kullanıcılar için çekim ipuçları ve en iyi fotoğraf noktaları, son paragraf pratik bilgiler (ziyaret saatleri, ulaşım, yakındaki diğer noktalar vb.) olmalı.",
                "summary": "Sosyal medya paylaşımı için 2-3 cümlelik çarpıcı özet",
                "keywords": ["Konum ile ilgili aramalar için anahtar kelimeler"],
                "suggested_category": "TRAVEL, FOOD, CULTURE, ADVENTURE veya OTHER",
                "location": {
                    "name": "Tam konum adı (örn: Galata Kulesi)",
                    "city": "Şehir",
                    "country": "Ülke",
                    "latitude": Enlem (örn: 41.0256),
                    "longitude": Boylam (örn: 28.9741),
                    "best_time_to_visit": "En iyi ziyaret zamanı",
                    "photo_spots": ["En iyi fotoğraf çekim noktaları"],
                    "nearby_attractions": ["Yakındaki diğer gezilecek yerler"],
                    "tips": ["Ziyaretçiler için önemli ipuçları"]
                }
            }

            ÖNEMLİ:
            - Sosyal medya kullanıcılarının ilgisini çekecek şekilde yaz
            - Fotoğraf çekim önerilerinde bulun
            - Konum bilgilerini mümkün olduğunca spesifik ver
            - Yakındaki diğer ilgi çekici yerleri mutlaka belirt
            - Koordinatları gerçeğe en yakın şekilde ver (bilmiyorsan yaklaşık değer kullanabilirsin)
            """
            
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format or 'JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            response = model.generate_content(
                contents=[
                    prompt,
                    {"mime_type": "image/jpeg", "data": img_byte_arr}
                ]
            )
            
            if response.text:
                clean_text = response.text.replace('```json', '').replace('```', '').strip()
                
                try:
                    ai_response = json.loads(clean_text)
                    
                    # Keywords'ü liste formatına çevir (eğer string gelirse)
                    if isinstance(ai_response.get('keywords'), str):
                        ai_response['keywords'] = [k.strip() for k in ai_response['keywords'].split(',')]
                    
                    # Location bilgilerinin kontrolü ve düzenlenmesi
                    location_data = ai_response.get('location', {})
                    if location_data:
                        try:
                            location_data['latitude'] = float(location_data.get('latitude', 0))
                            location_data['longitude'] = float(location_data.get('longitude', 0))
                            
                            # Listelerin string olarak gelmesi durumunda düzeltme
                            for list_field in ['photo_spots', 'nearby_attractions', 'tips']:
                                if isinstance(location_data.get(list_field), str):
                                    location_data[list_field] = [spot.strip() for spot in location_data[list_field].split(',')]
                        except (ValueError, TypeError):
                            location_data['latitude'] = 0
                            location_data['longitude'] = 0
                    
                    return Response({
                        'status': 'success',
                        'message': 'Görsel analizi başarılı',
                        'data': {
                            'title': ai_response.get('title'),
                            'content': ai_response.get('content'),
                            'summary': ai_response.get('summary'),
                            'keywords': ai_response.get('keywords'),
                            'suggested_category': ai_response.get('suggested_category', 'OTHER'),
                            'location': location_data
                        }
                    }, status=status.HTTP_200_OK)
                    
                except json.JSONDecodeError as e:
                    print(f"JSON parse hatası: {e}")
                    print("AI yanıtı:", response.text)
                    
            return Response({
                'status': 'error',
                'message': 'Görsel analizi başarısız oldu'
            }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"Görsel analizi hatası: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Görsel analizi sırasında beklenmeyen bir hata oluştu'
            }, status=status.HTTP_400_BAD_REQUEST)

class GlobalSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            search_query = request.query_params.get('q', '').strip()
            if not search_query or len(search_query) < 2:
                return Response({
                    'query': '',
                    'users': [],
                    'posts': [],
                    'categories': []
                })

            # Kullanıcı araması
            users = User.objects.annotate(
                similarity=Greatest(
                    TrigramSimilarity('username', search_query),
                    TrigramSimilarity('first_name', search_query),
                    TrigramSimilarity('last_name', search_query),
                    TrigramSimilarity('location', search_query)
                )
            ).filter(
                Q(similarity__gt=0.1) |  # En az %10 benzerlik
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            ).order_by('-similarity')[:5]

            # Post araması
            posts = BlogPost.objects.annotate(
                similarity=Greatest(
                    TrigramSimilarity('title', search_query),
                    TrigramSimilarity('summary', search_query),
                    TrigramSimilarity('tags', search_query),
                    TrigramSimilarity('location', search_query),
                    TrigramSimilarity('content', search_query)
                )
            ).filter(
                Q(similarity__gt=0.1) |  # En az %10 benzerlik
                Q(title__icontains=search_query) |
                Q(tags__icontains=search_query) |
                Q(location__icontains=search_query),
                is_published=True,
                is_approved=True
            ).select_related(
                'author',
                'category'
            ).order_by('-similarity')[:10]

            # Kategori araması
            categories = Category.objects.annotate(
                similarity=Greatest(
                    TrigramSimilarity('name', search_query),
                    TrigramSimilarity('description', search_query)
                )
            ).filter(
                Q(similarity__gt=0.1) |
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            ).order_by('-similarity')[:5]

            return Response({
                'query': search_query,
                'users': [{
                    'id': user.id,
                    'username': user.username,
                    'full_name': f"{user.first_name} {user.last_name}".strip(),
                    'profile_picture': user.profile_picture.url if user.profile_picture else None,
                    'location': user.location,
                    'total_posts': BlogPost.objects.filter(
                        author=user,
                        is_published=True,
                        is_approved=True
                    ).count(),
                    'similarity': round(user.similarity * 100, 2)
                } for user in users],
                'posts': [{
                    'id': post.id,
                    'title': post.title,
                    'summary': post.summary[:150] + '...' if post.summary else None,
                    'cover_image': post.cover_image.url if post.cover_image else None,
                    'author': {
                        'id': post.author.id,
                        'username': post.author.username,
                        'profile_picture': post.author.profile_picture.url if post.author.profile_picture else None
                    },
                    'category': {
                        'id': post.category.id,
                        'name': post.category.name
                    } if post.category else None,
                    'location': post.location,
                    'created_at': post.created_at,
                    'read_count': post.read_count,
                    'like_count': post.like_count,
                    'comment_count': post.comments.count(),
                    'tags': post.tags.split(',') if post.tags else [],
                    'similarity': round(post.similarity * 100, 2)
                } for post in posts],
                'categories': [{
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'post_count': BlogPost.objects.filter(
                        category=category,
                        is_published=True,
                        is_approved=True
                    ).count(),
                    'similarity': round(category.similarity * 100, 2)
                } for category in categories]
            })

        except Exception as e:
            print(f"Arama hatası: {str(e)}")
            return Response({
                'error': 'Arama sırasında bir hata oluştu',
                'message': str(e)
            }, status=500)
