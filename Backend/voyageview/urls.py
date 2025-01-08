from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger Şema Ayarları
schema_view = get_schema_view(
    openapi.Info(
        title="VoyageView API",
        default_version='v1',
        description="VoyageView Projesi için API dokümantasyonu",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@voyageview.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# URL Desenleri
urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # Kullanıcı Yönetimi
    path('blog/', include('blog.urls')),  # Blog Yönetimi
    path('notifications/', include('notifications.urls')), #Bildirim Yönetimi
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Medya Dosyaları
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
