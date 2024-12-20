from rest_framework.generics import ListAPIView
from backend.models import Post
from backend.serializers import PostSerializer
from django.utils.timezone import now
from datetime import timedelta

class FeaturedPostsView(ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        time_period = self.request.query_params.get('time_period', 'week')
        if time_period == 'week':
            start_date = now() - timedelta(days=7)
        elif time_period == 'month':
            start_date = now() - timedelta(days=30)
        else:
            start_date = None

        queryset = Post.objects.all()
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        return queryset.annotate(total_likes=Count('likes')).order_by('-total_likes')
