from django.urls import path
from backend.admin_panel.report import ReportListView, ReportCreateView
from backend.admin_panel.leaderboard import LeaderboardView
from backend.admin_panel.analytics import AnalyticsView
from backend.admin_panel.prominent_users import ProminentUsersView

urlpatterns = [
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('reports/create/', ReportCreateView.as_view(), name='report-create'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('prominent-users/', ProminentUsersView.as_view(), name='prominent-users'),
]
