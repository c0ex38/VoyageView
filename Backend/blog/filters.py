import django_filters
from .models import BlogPost

class BlogPostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    content = django_filters.CharFilter(field_name="content", lookup_expr="icontains")
    tags = django_filters.CharFilter(field_name="tags", lookup_expr="icontains")
    category = django_filters.CharFilter(field_name="category__name", lookup_expr="icontains")
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")
    popular = django_filters.OrderingFilter(
        fields=(
            ('like_count', 'like_count'),
            ('created_at', 'created_at'),
        ),
    )

    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'tags', 'category', 'created_at', 'popular']
