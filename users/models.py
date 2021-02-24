from django.db import models
from django.contrib.auth.models import User
from discord_bot.models import Guild


class MyUser(User):

    # LIFX stuff
    lifx_dev_token = models.CharField(max_length=100, blank=True)
    lifx_access_token = models.CharField(max_length=100, blank=True)
    lifx_refresh_token = models.CharField(max_length=100, blank=True)
    lifx_lights_list = models.JSONField(blank=True, default=dict)

    # Discord stuff
    discord_tag = models.CharField(max_length=100)
    # List of discord guilds that have been enabled by the user
    enabled_discord_guilds = models.ManyToManyField(Guild)
