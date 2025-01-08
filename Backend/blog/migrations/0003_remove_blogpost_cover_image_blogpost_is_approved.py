# Generated by Django 5.1.4 on 2025-01-04 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_blogpost_cover_image_blogpost_is_published_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpost',
            name='cover_image',
        ),
        migrations.AddField(
            model_name='blogpost',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
