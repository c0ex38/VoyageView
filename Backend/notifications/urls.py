from django.urls import path
from .views import NotificationListView, MarkNotificationAsReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),
    path('<int:notification_id>/read/', MarkNotificationAsReadView.as_view(), name='mark_notification_as_read'),
]
