import pathlib
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
import json
import django
django.setup()
from users.models import MyUser
from lights.models import LIFXLight
from asgiref.sync import sync_to_async


dotenv_path = pathlib.Path("..")
load_dotenv()


client = commands.Bot(command_prefix="$")


@client.event
async def on_ready():
    print("Bot is ready.")


@client.event
async def on_message(message: discord.Message):
    if message.mentions:
        for discord_user in message.mentions:
            try:
                user_from_db = await sync_to_async(MyUser.objects.get)(
                    discord_tag=str(discord_user)
                )
                discord_bulbs = await sync_to_async(get_discord_bulbs)(
                    user_from_db
                )
                for bulb in discord_bulbs:
                    await do_effects(bulb, user_from_db)
            except MyUser.DoesNotExist as e:
                continue


async def do_effects(bulb: LIFXLight, user: MyUser):
    effect = bulb.effect
    color = bulb.effect_color
    effects_settings = {
        "breathe_data": {"period": 1, "cycles": 5, "color": color, "peak": 1},
        "pulse_data": {"color": color, "cycles": 5, "persist": False,
                       "power_on": True}}
    headers = {"Authorization": f"Bearer {user.lifx_dev_token}"}
    resp = requests.post(
        f"https://api.lifx.com/v1/lights/id:{bulb.light_id}/effects/{effect}",
        data=json.dumps(effects_settings[f"{effect}_data"]), headers=headers)
    return resp.status_code


def get_discord_bulbs(user: MyUser):
    ret = []
    for bulb in user.lifxlight_set.all():
        if bulb.discord_enabled:
            ret.append(bulb)
    return ret


client.run(os.getenv("DISCORD_BOT_TOKEN"))
