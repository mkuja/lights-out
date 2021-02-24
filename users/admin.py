from django.contrib import admin
from users.models import MyUser
from discord_bot.models import Guild

# Register your models here.
admin.register(MyUser)
admin.register(Guild)
