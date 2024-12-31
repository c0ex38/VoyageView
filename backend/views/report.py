from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from backend.models import Report
from backend.serializers import ReportSerializer

class ReportCreateView(generics.CreateAPIView):
    """
    Kullanıcıların rapor oluşturabileceği endpoint.
    - Kullanıcılar, raporlarını oluşturduğunda, rapor kullanıcı bilgisi otomatik olarak eklenir.
    """
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]  # Yalnızca giriş yapmış kullanıcılar rapor oluşturabilir

    def perform_create(self, serializer):
        """
        Raporu kaydederken, giriş yapan kullanıcıyı otomatik olarak ekler.
        """
        serializer.save(user=self.request.user)

class ReportListView(generics.ListAPIView):
    """
    Yöneticilerin tüm raporları listeleyebileceği endpoint.
    - Raporlar, tipine ve sebebine göre filtrelenebilir.
    - Ayrıca raporlar, oluşturulma tarihine göre sıralanabilir.
    """
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]  # Yalnızca yöneticiler raporları görebilir
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]  # Filtreleme ve sıralama
    filterset_fields = ['report_type', 'reason']  # Rapor türü ve sebebine göre filtreleme
    ordering_fields = ['created_at']  # Sıralama alanları (oluşturulma tarihine göre)
    ordering = ['-created_at']  # Varsayılan sıralama (en yeni raporlar en üstte)
    search_fields = ['reason', 'user__username']  # Arama alanları

    def get_queryset(self):
        """
        Tüm raporları döndüren sorgu.
        """
        return Report.objects.all()
