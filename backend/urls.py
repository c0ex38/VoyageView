from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from backend.user.auth.register import RegisterUserAPIView
from backend.user.auth.verified_email import VerifyEmailAPIView
from backend.user.auth.resend_email import ResendVerificationCodeAPIView
from backend.user.auth.login import LoginUserAPIView
from backend.views.profile import ProfileDetailView
from backend.views.post import PostListCreateView, PostRetrieveUpdateDestroyView, PostLikeToggleView
from backend.views.follow import FollowedUsersPostListView
from backend.views.comment import CommentListCreateView, CommentDestroyView, CommentLikeToggleView
from backend.views.notification import NotificationListView, NotificationMarkAsReadView
from backend.views.report import ReportCreateView, ReportListView
from backend.views.leaderboard import LeaderboardView
from backend.views.analytics import AnalyticsView
from backend.views.featured import FeaturedPostsView, PersonalizedFeedView, TrendingPostsView, MostCommentedPostsView, RecentPostsView
from backend.views.prominent_users import ProminentUsersView
from backend.views.message import MessageListCreateView, MessageMarkAsReadView
from backend.views.share_post import SharePostView
from backend.views.message_group import GroupChatCreateView, GroupInviteView, GroupInvitationResponseView

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('login/', LoginUserAPIView.as_view(), name='login'),
    path('verify-email/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('resend-verification-code/', ResendVerificationCodeAPIView.as_view(), name='resend-verification-code'),
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
    path('home/feed/', PersonalizedFeedView.as_view(), name='personalized-feed'),
    path('home/trending/', TrendingPostsView.as_view(), name='trending-posts'),
    path('home/most-commented/', MostCommentedPostsView.as_view(), name='most-commented-posts'),
    path('home/recent/', RecentPostsView.as_view(), name='recent-posts'),
    path('prominent-users/', ProminentUsersView.as_view(), name='prominent-users'),
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/mark-read/', MessageMarkAsReadView.as_view(), name='message-mark-as-read'),
    path('share-post/', SharePostView.as_view(), name='share-post'),
    path('group-chats/', GroupChatCreateView.as_view(), name='group-create'),
    path('group-chats/<int:group_id>/invite/', GroupInviteView.as_view(), name='group-invite'),
    path('group-invitations/<int:invitation_id>/respond/', GroupInvitationResponseView.as_view(), name='group-invitation-respond'),
]