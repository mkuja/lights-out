from django.db import models
from django.contrib.auth.models import User


class MyUser(User):
    discord_tag = models.CharField(max_length=100)
    lifx_dev_token = models.CharField(max_length=100, blank=True)
    lifx_access_token = models.CharField(max_length=100, blank=True)
    lifx_refresh_token = models.CharField(max_length=100, blank=True)
    lifx_lights_list = models.JSONField(blank=True, default=dict)


