
from django.db import models
from django.contrib import admin
from django.contrib.postgres.fields import ArrayField


class Guild(models.Model):
    """Discord guilds aka. servers."""

    guild_id = models.CharField(max_length=70)
    guild_name = models.CharField(max_length=100)

    class Meta:
        app_label = "users"


admin.register(Guild)
