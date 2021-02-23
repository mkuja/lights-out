"""discord_bot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, label='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), label='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from about import views as about_views
from users import views as users_views
from lights import views as lights_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", about_views.landing_page, name="landing_page"),
    path("sign_up/", users_views.sign_up_user, name="sign_up_user"),
    path("sign_in/", users_views.sign_in_user, name="sign_in_user"),
    path("sign_out/", users_views.sign_out_user, name="sign_out_user"),
    path("edit_user/", users_views.edit_user, name="edit_user"),
    path("your_lights/", lights_views.your_lights, name="your_lights"),
    path("get_lights_list/", lights_views.get_lights_list,
         name="get_lights_list"),
    path("test_and_save_light/", lights_views.test_and_save_light,
         name="test_and_save_light"),
    path("delete_light/", lights_views.delete_light, name="delete_light")
]
