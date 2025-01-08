from django.urls import path
from backend.notification.notification import NotificationListView, NotificationMarkAsReadView, NotificationMarkAllAsReadView, NotificationUnreadCountView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', NotificationMarkAsReadView.as_view(), name='notification-mark-read'),
    path('mark-all-read/', NotificationMarkAllAsReadView.as_view(), name='notification-mark-all-read'),
    path('unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
]
