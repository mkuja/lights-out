# Generated by Django 3.1.7 on 2021-02-23 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lights', '0002_auto_20210223_0235'),
    ]

    operations = [
        migrations.AddField(
            model_name='lifxlight',
            name='discord_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='lifxlight',
            name='effect',
            field=models.CharField(default='breath', max_length=50),
        ),
    ]