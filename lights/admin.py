from django.contrib import admin
from users.models import MyUser
from lights.models import LIFXLight


admin.site.register(MyUser)
admin.site.register(LIFXLight)
