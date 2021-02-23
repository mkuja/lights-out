import pathlib
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from users.models import MyUser


dotenv_path = pathlib.Path("..")
load_dotenv()


client = commands.Bot(command_prefix="$")


@client.event
async def on_ready():
    print("Bot is ready.")


@client.event
async def on_message(message: discord.Message):
    for user in message.mentions:
        print(user)


async def get_lifx_lights(user: discord.User):
    pass

client.run(os.getenv("DISCORD_BOT_TOKEN"))
