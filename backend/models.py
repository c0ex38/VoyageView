from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils.timezone import now
import tempfile
import cv2

class SharedPost(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_posts")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_posts")
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class GroupChat(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name="group_chats")
    admins = models.ManyToManyField(User, related_name="admin_groups")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GroupInvitation(models.Model):
    group = models.ForeignKey(GroupChat, related_name="invitations", on_delete=models.CASCADE)
    invited_user = models.ForeignKey(User, related_name="group_invitations", on_delete=models.CASCADE)
    invited_by = models.ForeignKey(User, related_name="sent_invitations", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return f"Invitation to {self.invited_user} for {self.group}"

class GroupMessage(models.Model):
    group = models.ForeignKey(GroupChat, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}"


    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} at {self.timestamp}"
        
class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=now)

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
    is_email_verified = models.BooleanField(default=False)
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
    image = models.ImageField(upload_to='post_images/', blank=False, null=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location_name = models.CharField(max_length=255)  # Lokasyon adı
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    latitude = models.FloatField(blank=False, null=False)  # Enlem
    longitude = models.FloatField(blank=False, null=False)  # Boylam
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('Tag', related_name='posts', blank=True)

    def location(self):
        return f"{self.latitude}, {self.longitude}"

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

class UserInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=50, choices=[
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('view', 'View'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
