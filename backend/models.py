from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils.timezone import now
import tempfile
import cv2

class Badge(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Rozet adı
    description = models.TextField(blank=True, null=True)  # Açıklama
    level_requirement = models.PositiveIntegerField()  # Seviyeye göre gereklilik
    icon = models.ImageField(upload_to='badge_icons/', blank=True, null=True)  # Rozet simgesi

    def __str__(self):
        return f"{self.name} (Level {self.level_requirement})"

class Report(models.Model):
    REPORT_TYPES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
    ]

    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('abuse', 'Abuse'),
        ('inappropriate', 'Inappropriate Content'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    reason = models.CharField(max_length=50, choices=REPORT_REASONS)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_type.capitalize()} Report by {self.user.username}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} from {self.sender.username}"

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    social_link = models.URLField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    followers = models.ManyToManyField('self', related_name='following', symmetrical=False, blank=True)
    level = models.PositiveIntegerField(default=1)
    points = models.PositiveIntegerField(default=0)
    badges = models.ManyToManyField(Badge, related_name="users", blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def update_level(self):
        """Kullanıcının seviyesini günceller."""
        self.level = (self.points // 100) + 1  # 100 puan = 1 seviye
        self.save()

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

def validate_video_duration(media_file):
    # Geçici dosya oluştur
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(media_file.read())  # Dosyayı geçici dosyaya yaz
        temp_file.flush()  # Diskte saklandığından emin olun
        file_path = temp_file.name

    # OpenCV kullanarak video süresini kontrol et
    video = cv2.VideoCapture(file_path)
    if not video.isOpened():
        raise ValueError("Video file could not be opened.")

    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps if fps > 0 else 0
    video.release()

    # Geçici dosyayı sil
    temp_file.close()

    if duration > 15:
        raise ValueError("Video duration exceeds the limit of 15 seconds.")

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('cultural', 'Cultural Place'),
        ('touristic', 'Touristic Place'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    tags = models.ManyToManyField('Tag', related_name="posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class PostMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    file = models.FileField(upload_to='post_media/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.media_type} for Post {self.post.title}"

class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)  # Beğeni alanı
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

