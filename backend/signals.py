from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from backend.models import Post, Comment, Profile, Badge

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.profile and (instance.profile.bio != instance.profile.bio or instance.profile.location != instance.profile.location):
        instance.profile.save()

@receiver(post_save, sender=Post)
def add_points_for_post(sender, instance, created, **kwargs):
    if created:
        profile = instance.author.profile
        profile.points += 10  # Post başına 10 puan
        profile.save()  # Yalnızca puan değiştikten sonra kaydediyoruz

@receiver(post_save, sender=Comment)
def add_points_for_comment(sender, instance, created, **kwargs):
    if created:
        profile = instance.author.profile
        profile.points += 5  # Yorum başına 5 puan
        profile.save()  # Yalnızca puan değiştikten sonra kaydediyoruz

@receiver(post_save, sender=Profile)
def assign_badges(sender, instance, **kwargs):
    """Kullanıcı seviyesi rozet gerekliliğini karşıladığında rozet ekler."""
    previous_level = instance.level
    instance.refresh_from_db()  # Veritabanından en güncel verileri al

    # Seviyede değişiklik varsa sadece yeni seviyeye uygun rozetleri kontrol et
    if instance.level != previous_level:
        # Eski seviyeye ait rozetleri kaldırabiliriz (isteğe bağlı)
        instance.badges.clear()

        # Yeni seviyeye uygun rozetleri al
        available_badges = Badge.objects.filter(level_requirement__lte=instance.level)
        for badge in available_badges:
            if badge not in instance.badges.all():
                instance.badges.add(badge)
