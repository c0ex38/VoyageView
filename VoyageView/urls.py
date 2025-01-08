from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.i18n import set_language

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin paneli
    path('auth/', include('backend.urls.auth')),  # Authentication
    path('profile/', include('backend.urls.profile')),  # Profile
    path('posts/', include('backend.urls.post')),  # Posts
    path('notifications/', include('backend.urls.notification')),  # Notifications
    path('home/', include('backend.urls.home')),  # Home (featured, personalized, trending, etc.)
    path('messages/', include('backend.urls.message')),  # Messages
    path('search/', include('backend.urls.search')) # Search
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Medya dosyaları için static

# Dil ayarı için URL
urlpatterns += [
    path('set_language/', set_language, name='set_language'),
]
