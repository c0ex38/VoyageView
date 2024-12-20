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
from backend.views.notification import NotificationListView, NotificationMarkAsReadView
from backend.views.report import ReportCreateView, ReportListView
from backend.views.leaderboard import LeaderboardView
from backend.views.analytics import AnalyticsView
from backend.views.featured import FeaturedPostsView
from backend.views.prominent_users import ProminentUsersView

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
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', NotificationMarkAsReadView.as_view(), name='notification-mark-read'),
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('reports/create/', ReportCreateView.as_view(), name='report-create'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('featured-posts/', FeaturedPostsView.as_view(), name='featured-posts'),
    path('prominent-users/', ProminentUsersView.as_view(), name='prominent-users'),
]