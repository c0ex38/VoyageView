from datetime import datetime
from django.db import models
from django.db.models import Count, Sum
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from backend.models import Profile, Post
from backend.serializers import ProfileSerializer
from django.utils.dateparse import parse_date

class LeaderboardView(ListAPIView):
    """
    Kullanıcıların liderlik tablosunu listeleyen API.
    - Kullanıcıların seviyelerine göre sıralanır.
    - Filtreleme, sıralama ve sayfalama yapılabilir.
    """
    serializer_class = ProfileSerializer
    pagination_class = PageNumberPagination  # Sayfalandırma ekleniyor

    def get_queryset(self):
        """
        Liderlik tablosu için sorgu oluşturur.
        - Kullanıcıları sıralar, filtreler ve kategorilere göre gruplar.
        - İsteğe bağlı olarak, en iyi postlara göre sıralama yapar.
        """
        queryset = Profile.objects.all()  # Tüm profilleri alıyoruz

        # Tarih filtreleme
        start_date = self.request.query_params.get('start_date')  # Başlangıç tarihi
        end_date = self.request.query_params.get('end_date')  # Bitiş tarihi

        if start_date:
            start_date = parse_date(start_date)  # Başlangıç tarihini parse ediyoruz
            queryset = queryset.filter(user__posts__created_at__gte=start_date)  # Başlangıç tarihinden sonra olan postlar
        if end_date:
            end_date = parse_date(end_date)  # Bitiş tarihini parse ediyoruz
            queryset = queryset.filter(user__posts__created_at__lte=end_date)  # Bitiş tarihinden önce olan postlar

        # En iyi postlar sıralaması
        best_posts = self.request.query_params.get('best_posts', 'false').lower()
        if best_posts == 'true':
            # En fazla beğeniye sahip postları sıralıyoruz
            queryset = queryset.annotate(total_likes=Sum('user__posts__likes')).order_by('-total_likes')

        # Kategori filtreleme
        category = self.request.query_params.get('category')
        if category:
            # Kategoriye göre filtreleme yapıyoruz
            queryset = queryset.filter(user__posts__category=category)

        # Varsayılan sıralama
        # Kategoriye göre sıralama yapılır ve toplam beğenilere göre en yüksek profillere göre sıralanır
        return queryset.annotate(points_sum=Sum('user__posts__likes')).order_by('-level', '-points_sum')

    def list(self, request, *args, **kwargs):
        """
        Yanıt verilerini yapılandırır.
        - Filtreleri ve sonuçları bir arada döndürür.
        """
        response = super().list(request, *args, **kwargs)  # Listeleme işlemi
        response.data = {
            "filters": {
                "start_date": self.request.query_params.get('start_date', None),  # Başlangıç tarihi
                "end_date": self.request.query_params.get('end_date', None),  # Bitiş tarihi
                "best_posts": self.request.query_params.get('best_posts', 'false'),  # En iyi postlar
                "category": self.request.query_params.get('category', None),  # Kategori
            },
            "results": response.data  # Sonuçları ekliyoruz
        }
        return Response(response.data)  # Yanıtı döndürüyoruz
