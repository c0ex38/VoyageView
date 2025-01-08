from django.urls import path
from backend.post.post import PostListCreateView, PostRetrieveUpdateDestroyView, PostLikeToggleView
from backend.post.comment import CommentListCreateView, CommentUpdateView, CommentDestroyView, CommentLikeToggleView

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list-create'),
    path('<int:pk>/', PostRetrieveUpdateDestroyView.as_view(), name='post-detail'),
    path('<int:pk>/like/', PostLikeToggleView.as_view(), name='post-like-toggle'),
    path('<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/update/', CommentUpdateView.as_view(), name='comment-update'),
    path('comments/<int:pk>/', CommentDestroyView.as_view(), name='comment-destroy'),
    path('comments/<int:pk>/like/', CommentLikeToggleView.as_view(), name='comment-like-toggle'),
]
