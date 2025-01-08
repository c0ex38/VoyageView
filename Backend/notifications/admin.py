from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'short_message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    actions = ['mark_as_read', 'mark_as_unread', 'delete_old_notifications']

    def short_message(self, obj):
        """Uzun mesajları kısaltarak göster"""
        return (obj.message[:50] + '...') if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Mesaj'

    @admin.action(description='Seçili bildirimleri okundu olarak işaretle')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} bildirim okundu olarak işaretlendi.')

    @admin.action(description='Seçili bildirimleri okunmadı olarak işaretle')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} bildirim okunmadı olarak işaretlendi.')

    @admin.action(description='30 günden eski okunmuş bildirimleri sil')
    def delete_old_notifications(self, request, queryset):
        from django.utils import timezone
        import datetime
        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
        deleted = queryset.filter(
            created_at__lt=thirty_days_ago,
            is_read=True
        ).delete()[0]
        self.message_user(request, f'{deleted} eski bildirim silindi.')

    fieldsets = (
        ('Bildirim Detayları', {
            'fields': ('user', 'message', 'is_read')
        }),
        ('Zaman Bilgisi', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Performans için ilişkili kullanıcı verilerini önceden yükle"""
        return super().get_queryset(request).select_related('user')

    def has_add_permission(self, request):
        """Sadece programatik olarak bildirim oluşturulabilir"""
        return False
