from django.contrib import admin
from .models import (
    Badge, Tag, PasswordHistory, Profile, Post, PostMedia, Comment, Follow, 
    SharedPost, UserInteraction, Notification, Report, GroupChat, GroupInvitation,
    GroupMessage, Message, EmailVerification
)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'level_requirement', 'badge_type')
    list_filter = ('level_requirement', 'badge_type')
    search_fields = ('name', 'description')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(PasswordHistory)
class PasswordHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_email_verified', 'location', 'birth_date', 'gender', 'created_at', 'level', 'points')
    list_filter = ('is_email_verified', 'gender', 'created_at', 'level')
    search_fields = ('user__username', 'location')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'updated_at', 'status', 'published_at', 'visibility')
    list_filter = ('category', 'status', 'visibility', 'created_at', 'updated_at', 'published_at')
    search_fields = ('title', 'description', 'author__username', 'location_name')
    actions = ['publish_posts', 'unpublish_posts']

    def publish_posts(self, request, queryset):
        queryset.update(status='published', published_at=timezone.now())
    publish_posts.short_description = "Publish selected posts"

    def unpublish_posts(self, request, queryset):  
        queryset.update(status='draft', published_at=None)
    unpublish_posts.short_description = "Unpublish selected posts"

class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('post__title', 'author__username', 'content')

@admin.register(Follow)  
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'followed_user', 'created_at')
    search_fields = ('user__username', 'followed_user__username')

@admin.register(SharedPost)
class SharedPostAdmin(admin.ModelAdmin):  
    list_display = ('post', 'sender', 'recipient', 'created_at')
    search_fields = ('post__title', 'sender__username', 'recipient__username')

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'interaction_type', 'created_at') 
    list_filter = ('interaction_type', 'created_at')
    search_fields = ('user__username', 'post__title')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'sender', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'sender__username')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'reason', 'status', 'created_at')
    list_filter = ('report_type', 'reason', 'status', 'created_at')  
    search_fields = ('user__username',)

@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    filter_horizontal = ('members', 'admins')
    search_fields = ('name',)

@admin.register(GroupInvitation) 
class GroupInvitationAdmin(admin.ModelAdmin):
    list_display = ('group', 'invited_user', 'invited_by', 'created_at', 'is_accepted', 'is_rejected')
    list_filter = ('created_at', 'is_accepted', 'is_rejected')
    search_fields = ('group__name', 'invited_user__username', 'invited_by__username')

@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'created_at')
    search_fields = ('group__name', 'sender__username', 'content')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):  
    list_display = ('sender', 'recipient', 'created_at', 'is_read', 'is_archived')
    list_filter = ('created_at', 'is_read', 'is_archived')
    search_fields = ('sender__username', 'recipient__username', 'content')

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_code', 'created_at')
    search_fields = ('user__username', 'verification_code')