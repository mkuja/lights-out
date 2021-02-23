from django.db import models
from users.models import MyUser


class LIFXLight(models.Model):
    light_id = models.CharField(max_length=100)
    uuid = models.CharField(max_length=100)
    label = models.CharField(max_length=100)
    group_name = models.CharField(max_length=100, blank=True)
    json = models.JSONField()
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    # Settings
    effect = models.CharField(max_length=50, blank=True)
    effect_color = models.CharField(max_length=10, default="#FF0000")
    discord_enabled = models.BooleanField(default=False)
