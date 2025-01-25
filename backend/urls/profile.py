from django.urls import path
from backend.profile.profile import ProfileDetailView
from backend.profile.check_user_status import CheckUserStatusAPIView
from backend.profile.user_id import GetUserIdAPIView
from backend.profile.follow import FollowedUsersPostListView, FollowToggleView, FollowedUsersView, FollowersView

urlpatterns = [
    path('', ProfileDetailView.as_view(), name='profile-detail'),
    path('check-user-status/', CheckUserStatusAPIView.as_view(), name='check-user-status'),
    path('get-user-id/', GetUserIdAPIView.as_view(), name='get-user-id'),
    path('followed-posts/', FollowedUsersPostListView.as_view(), name='followed-posts'),
    path('follow-toggle/', FollowToggleView.as_view(), name='follow-toggle'),
    path('followed-users/', FollowedUsersView.as_view(), name='followed-users'),
    path('followers/', FollowersView.as_view(), name='followers'),
]
