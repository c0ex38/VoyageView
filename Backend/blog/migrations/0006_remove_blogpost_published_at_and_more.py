# Generated by Django 5.1.4 on 2025-01-04 03:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_category_blogpost_is_featured_blogpost_published_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpost',
            name='published_at',
        ),
        migrations.RemoveField(
            model_name='blogpost',
            name='seo_description',
        ),
        migrations.RemoveField(
            model_name='blogpost',
            name='seo_title',
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='blog.category'),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=100, unique=True),
        ),
    ]
