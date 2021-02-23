import requests
import json

from aiohttp.web_exceptions import HTTPMethodNotAllowed
from django.contrib.auth import get_user
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from users.models import MyUser
from lights.models import LIFXLight


def your_lights(request, context=None):

    user = get_user(request)
    my_user = MyUser.objects.filter(username=user.get_username()).first()
    context = {
        "authenticated": user.is_authenticated,
        "active_page": "my_lights",
        "username": user.get_username(),
        "lights": LIFXLight.objects.filter(user=my_user).all()
    }
    return render(request, "lights/your_lights.html", context)


def get_lights_list(request):

    def save_lights(lights, user: MyUser):

        for light in lights:
            try:
                # First line raises LIFXLight.DoesNotExist unless it exists.
                old_light = user.lifxlight_set.get(light_id=light["id"])
                old_light.light_id = light["id"]
                old_light.uuid = light["uuid"]
                old_light.label = light["label"]
                old_light.group_name = light["group"]["name"]
                old_light.json = json.dumps(lights)

            # Create since it doesn't exist.
            except LIFXLight.DoesNotExist as e:
                db_light = LIFXLight.objects.create(
                    light_id=light["id"],
                    uuid=light["uuid"],
                    label=light["label"],
                    group_name=light["group"]["name"],
                    user=user,
                    json=json.dumps(lights))
                db_light.save()

    user = get_user(request)
    my_user = MyUser.objects.filter(username=user.get_username()).first()
    token = my_user.lifx_dev_token
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get('https://api.lifx.com/v1/lights/all',
                        headers=headers)
    context = {
        "authenticated": user.is_authenticated,
        "active_page": "my_lights",
        "username": user.get_username()
    }
    if resp.status_code == 200:
        # OK
        save_lights(resp.json(), my_user)
        context.update(
            {"lights": LIFXLight.objects.filter(user=my_user).all()}
        )
    else:
        # Something unexpected happened.
        context.update({"error": resp.status_code})
    return render(request, "lights/your_lights.html", context)


def test_and_save_light(request):
    # Make sure user is logged in and owns the tested light.
    user = get_user(request)
    my_user = MyUser.objects.get(username=user.get_username())
    light_id = request.POST["id"]
    color = request.POST["color"]
    bulb = [x for x in my_user.lifxlight_set.all() if x.light_id == light_id]
    bulb = None if not bulb else bulb[0]

    data = {
        "breathe_data": {"period": 1, "cycles": 5, "color": color, "peak": 1},
        # "move_data": {"period": 10, "cycles": 1, "direction": "backward", },
        # "morph_data": {"power_on": True, "duration": 6, "period": 1,
        #                "palette": ["red", "green", "blue"]},
        #"flame_data": {"power_on": True},
        "pulse_data": {"color": color, "cycles": 5,
                       "persist": False, "power_on": True}
    }

    # User owns the bulb and is authenticated.
    if user.is_authenticated and bulb:
        # Test the bulb.
        effect = request.POST["effect"]
        checkbox = request.POST.get("discord_enabled")
        discord_enabled = True if checkbox else False
        bulb.effect = effect
        bulb.discord_enabled = discord_enabled
        bulb.effect_color = color
        bulb.save()
        token = my_user.lifx_dev_token
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(
            f"https://api.lifx.com/v1/lights/id:{bulb.light_id}/effects/{effect}",
            data=json.dumps(data[f"{effect}_data"]), headers=headers)
        if resp.status_code == 207:
            return redirect("get_lights_list")
        else:
            return render(request, "lights/effects_error.html",
                          {"response": resp,
                           "authenticated": True})
    else:
        return HttpResponseForbidden


def delete_light(request):
    if request.method == "POST":
        delete_id = request.POST["light_id"]
        bulb = LIFXLight.objects.get(light_id=delete_id)
        user = get_user(request)
        if (user.is_authenticated
                and bulb.user.get_username() == user.get_username()):
            LIFXLight.objects.filter(light_id=delete_id).delete()
            return redirect("your_lights")
        else:
            return HttpResponseForbidden
    else:
        return HTTPMethodNotAllowed
