# Generated by Django 5.1.4 on 2024-12-31 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0016_alter_profile_level_alter_profile_points'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.CharField(choices=[('cultural', 'Cultural Place'), ('touristic', 'Touristic Place'), ('technology', 'Technology'), ('sports', 'Sports'), ('art', 'Art'), ('nature', 'Nature'), ('historical', 'Historical Sites'), ('educational', 'Educational Institutions'), ('entertainment', 'Entertainment'), ('music', 'Music'), ('food', 'Food & Drink'), ('adventure', 'Adventure'), ('wellness', 'Wellness'), ('shopping', 'Shopping'), ('business', 'Business'), ('lifestyle', 'Lifestyle'), ('festival', 'Festival'), ('nightlife', 'Nightlife'), ('outdoor', 'Outdoor Activities'), ('religious', 'Religious Sites'), ('romantic', 'Romantic Getaways'), ('family', 'Family Activities')], max_length=20),
        ),
    ]
