from django.contrib import admin
from .models import BlogPost, Category, Like, Comment, Favorite

# Kategori Yönetimi
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

# Blog Yönetimi
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_approved', 'is_published', 'like_count', 'read_count', 'created_at']
    list_filter = ['is_approved', 'is_published', 'category', 'author', 'created_at']
    search_fields = ['title', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['read_count', 'like_count'] 
    actions = ['approve_posts']

    @admin.action(description='Seçili yazıları onayla ve yayınla')
    def approve_posts(self, request, queryset):
        queryset.update(is_approved=True, is_published=True)
        self.message_user(request, f"{queryset.count()} yazı onaylandı ve yayınlandı.")

# Beğeni Yönetimi
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'blog_post', 'created_at']
    search_fields = ['user__username', 'blog_post__title']
    list_filter = ['created_at']

# Yorum Yönetimi
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'blog_post', 'content', 'created_at']
    search_fields = ['user__username', 'blog_post__title', 'content']
    list_filter = ['created_at']

# Favori Yönetimi
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'blog_post', 'created_at']
    search_fields = ['user__username', 'blog_post__title']
    list_filter = ['created_at']
