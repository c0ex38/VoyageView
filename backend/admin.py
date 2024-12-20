from django.contrib import admin
from backend.models import Profile, Post, Comment, Tag, Notification, Report, Badge

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'birth_date', 'phone_number', 'gender', 'created_at']
    search_fields = ['user__username', 'location', 'bio']
    list_filter = ['created_at', 'gender']
    ordering = ['user__username']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'location', 'created_at')  # Alanlar burada belirtiliyor
    search_fields = ('title', 'description', 'location')  # Arama yapılabilir alanlar
    list_filter = ('category', 'created_at')  # Filtreleme için alanlar

    def author(self, obj):
        return obj.author.username  # Eğer `author` bir ForeignKey ise username döner
    author.short_description = 'Author'  # Admin'de başlık

    def location(self, obj):
        return f"{obj.latitude}, {obj.longitude}"  # Eğer tam nokta istiyorsanız
    location.short_description = 'Location'  # Admin'de başlık

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'content', 'parent', 'created_at']
    search_fields = ['author__username', 'content', 'post__title']
    list_filter = ['created_at']
    ordering = ['-created_at']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'sender', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'sender__username']
    ordering = ['-created_at']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'report_type', 'reason', 'post', 'comment', 'created_at']
    list_filter = ['report_type', 'reason', 'created_at']
    search_fields = ['user__username', 'reason', 'post__title', 'comment__content']
    ordering = ['-created_at']

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'level_requirement', 'description')
    search_fields = ('name', 'description')
    list_filter = ('level_requirement',)