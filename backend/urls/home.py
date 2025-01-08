from django.urls import path
from backend.home.featured import FeaturedPostsView, PersonalizedFeedView, TrendingPostsView, MostCommentedPostsView, RecentPostsView

urlpatterns = [
    path('featured-posts/', FeaturedPostsView.as_view(), name='featured-posts'),
    path('feed/', PersonalizedFeedView.as_view(), name='personalized-feed'),
    path('trending/', TrendingPostsView.as_view(), name='trending-posts'),
    path('most-commented/', MostCommentedPostsView.as_view(), name='most-commented-posts'),
    path('recent/', RecentPostsView.as_view(), name='recent-posts'),
]
