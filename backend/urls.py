from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from backend.user.auth.register import register_user
from backend.user.auth.login import login_user
from backend.views.profile import ProfileDetailView
from backend.views.post import PostListCreateView, PostRetrieveUpdateDestroyView, PostLikeToggleView, FollowedUsersPostListView
from backend.views.comment import CommentListCreateView, CommentDestroyView, CommentLikeToggleView

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileDetailView.as_view(), name='profile-detail'),
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostRetrieveUpdateDestroyView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDestroyView.as_view(), name='comment-destroy'),
    path('posts/<int:pk>/like/', PostLikeToggleView.as_view(), name='post-like-toggle'),
    path('comments/<int:pk>/like/', CommentLikeToggleView.as_view(), name='comment-like-toggle'),
    path('posts/followed/', FollowedUsersPostListView.as_view(), name='followed-posts'),
]
