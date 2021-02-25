from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from discord_bot.models import Guild


class MyUser(User):

    # LIFX stuff
    lifx_dev_token = models.CharField(max_length=100, blank=True)
    lifx_access_token = models.CharField(max_length=100, blank=True)
    lifx_refresh_token = models.CharField(max_length=100, blank=True)
    lifx_lights_list = models.JSONField(blank=True, default=list)

    # Discord stuff
    discord_tag = models.CharField(max_length=100, unique=True)
    # List of discord guilds that have been enabled by the user
    discord_enabled_guilds = models.ManyToManyField(Guild)
    discord_ignored_users = ArrayField(models.CharField(max_length=100),
                                       blank=True, default=list)
