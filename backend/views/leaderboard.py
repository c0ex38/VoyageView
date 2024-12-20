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
    serializer_class = ProfileSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Profile.objects.all()

        # Tarih filtreleme
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            start_date = parse_date(start_date)
            queryset = queryset.filter(user__posts__created_at__gte=start_date)
        if end_date:
            end_date = parse_date(end_date)
            queryset = queryset.filter(user__posts__created_at__lte=end_date)

        # En iyi postlar sıralaması
        best_posts = self.request.query_params.get('best_posts', 'false').lower()
        if best_posts == 'true':
            queryset = queryset.annotate(total_likes=Sum('user__posts__likes')).order_by('-total_likes')

        # Kategori filtreleme
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(user__posts__category=category)

        # Varsayılan sıralama
        return queryset.annotate(points_sum=Sum('user__posts__likes')).order_by('-level', '-points_sum')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            "filters": {
                "start_date": self.request.query_params.get('start_date', None),
                "end_date": self.request.query_params.get('end_date', None),
                "best_posts": self.request.query_params.get('best_posts', 'false'),
                "category": self.request.query_params.get('category', None),
            },
            "results": response.data
        }
        return Response(response.data)
