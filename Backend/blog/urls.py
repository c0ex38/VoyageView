from django.urls import path
from .views import (CategoryListCreateView, BlogPostListCreateView, BlogPostDetailView, PublishedBlogPostsView, 
                    LikeBlogPostView, CommentListCreateView, PopularBlogPostsView, MLPersonalizedPopularBlogPostsView,
                    FavoriteBlogPostView, CommentDetailView, ModerationCommentListView, ApproveCommentView,
                    BlogPostSearchFilterView, AddToReadingListView, ReadingListView, generate_summary,
                    ImageAnalysisView, GlobalSearchView)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category_list_create'),
    path('posts/', BlogPostListCreateView.as_view(), name='blogpost_list_create'),
    path('posts/<int:pk>/', BlogPostDetailView.as_view(), name='blogpost_detail'),
    path('posts/published/', PublishedBlogPostsView.as_view(), name='published_blogposts'),
    path('posts/<int:blog_post_id>/like/', LikeBlogPostView.as_view(), name='like_blog_post'),
    path('posts/<int:blog_post_id>/comments/', CommentListCreateView.as_view(), name='comment_list_create'),
    path('posts/comments/<int:pk>/', CommentDetailView.as_view(), name='comment_detail'),
    path('posts/comments/moderation/', ModerationCommentListView.as_view(), name='comment_moderation'),
    path('posts/comments/<int:pk>/approve/', ApproveCommentView.as_view(), name='approve_comment'),
    path('posts/<int:blog_post_id>/favorite/', FavoriteBlogPostView.as_view(), name='favorite_blog_post'),
    path('posts/popular/', PopularBlogPostsView.as_view(), name='popular_blogposts'),
    path('posts/ml-personalized-popular/', MLPersonalizedPopularBlogPostsView.as_view(), name='ml-personalized-popular-posts'),
    path('posts/search/', BlogPostSearchFilterView.as_view(), name='blogpost_search_filter'),
    path('posts/<int:blog_post_id>/reading-list/', AddToReadingListView.as_view(), name='add_to_reading_list'),
    path('users/reading-list/', ReadingListView.as_view(), name='reading_list'),
    path('generate-summary/', generate_summary, name='generate-summary'),
    path('analyze-image/', ImageAnalysisView.as_view(), name='analyze-image'),
    path('search/', GlobalSearchView.as_view(), name='global_search'),
]
