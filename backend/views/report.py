from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from backend.models import Report
from backend.serializers import ReportSerializer

class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReportListView(generics.ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report_type', 'reason']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    search_fields = ['reason', 'user__username']

    def get_queryset(self):
        return Report.objects.all()
