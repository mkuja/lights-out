import pathlib
import os
import discord
from typing import List
from discord.ext import commands
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
import requests
import json
import django
django.setup()
from lights.models import LIFXLight
from users.models import MyUser
from discord_bot.models import Guild


load_dotenv()


client = commands.Bot(command_prefix="$")


# TODO: Handle @here and @everyone


@client.event
async def on_ready():
    print("Bot is ready.")


# TODO: Test behavior when lights are not powered.
# TODO: Break it down a bit.
@client.event
async def on_message(message: discord.Message):
    """Watch all messages for mentions."""

    await client.process_commands(message)

    # Don't do anything else on bot-command.
    ctx: commands.Context = await client.get_context(message)
    if ctx.valid:
        return

    if message.mentions:
        for discord_user in message.mentions:
            # If user is in DB he is registered => Do checks & effects.
            try:
                mentioned_user_from_db: MyUser = await sync_to_async(
                    MyUser.objects.get)(discord_tag=str(discord_user))

                # Check that user has this guild enabled.
                users_guilds: List[Guild] = await sync_to_async(list)(
                    mentioned_user_from_db.discord_enabled_guilds.all())

                # It is registered user's mention. See if the guild is enabled.
                async for guild in list_muncher(users_guilds):
                    if guild.guild_id == str(message.guild.id):

                        # One last check, that user hasn't ignored this guy
                        # who is doing the mention.
                        ignored = await sync_to_async(list)(
                            mentioned_user_from_db.discord_ignored_users)

                        # List will be empty if author wasn't on the list.
                        if not [x
                                async for x in list_muncher(ignored)
                                if x == str(message.author)]:

                            # Get discord enabled bulbs and do effects.
                            discord_bulbs = await sync_to_async(
                                get_discord_bulbs)(mentioned_user_from_db)
                            for bulb in discord_bulbs:
                                await do_effects(bulb, mentioned_user_from_db)

            # Mentioned user isn't registered.
            except MyUser.DoesNotExist as _:
                continue
            except Guild.DoesNotExist as _:
                continue


@client.command(name="guilds")
async def guilds(ctx):
    """Command to get list of active guilds."""

    try:
        db_user = await sync_to_async(MyUser.objects.get)(
            discord_tag=str(ctx.author))
    except MyUser.DoesNotExist as _:
        ctx.send("You have to register first.")
        return
    user_guilds = await sync_to_async(list)(
        db_user.discord_enabled_guilds.all())
    msg = f"""{', '.join(
        [x.guild_name async for x in list_muncher(user_guilds)])}"""
    msg = "Guilds you've enabled: " + msg if msg else "No enabled guilds."
    await ctx.send(msg)


@client.command(name="ignore")
async def ignore(ctx, person: discord.Member = None):
    """Ignore a person."""

    if not person:
        await ctx.send("Person to be ignored needed as an argument.")
        return

    try:
        db_user: MyUser = await sync_to_async(
            MyUser.objects.get)(discord_tag=str(ctx.author))
    except MyUser.DoesNotExist as _:
        await ctx.send("You need to register first.")
        return

    ignored: List[str] = await sync_to_async(list)(
        db_user.discord_ignored_users)

    async for ignored_person in list_muncher(ignored):
        if str(person) == ignored_person:
            await ctx.send(f"You're already ignoring {str(person)}.")
            return
    else:
        await sync_to_async(db_user.discord_ignored_users.append)(str(person))
        await sync_to_async(db_user.save)()
        await ctx.send(
            f"Now ignoring light notifications from {str(person)}.")


@client.command(name="unignore")
async def unignore(ctx, person: discord.Member = None):
    """Unignore a person."""

    if not person:
        await ctx.send("Person to be unignored needed as an argument.")
        return

    try:
        db_user: MyUser = await sync_to_async(
            MyUser.objects.get)(discord_tag=str(ctx.author))
    except MyUser.DoesNotExist as _:
        await ctx.send("You're not even registered. You don't have ignores.")
        return

    ignored: List[str] = await sync_to_async(list)(
        db_user.discord_ignored_users)

    async for ignored_person in list_muncher(ignored):
        if str(person) == ignored_person:
            await sync_to_async(
                db_user.discord_ignored_users.remove)(ignored_person)
            await sync_to_async(db_user.save)()
            await ctx.send(f"Unignored {ignored_person} for you.")
            return
    await ctx.send(f"You haven't ignored {person}.")


# TODO: What if ignored person changes their tag? Should ID be used instead?
@client.command(name="ignore_list")
async def ignore_list(ctx):
    """Give ctx.author's ignore list."""

    try:
        db_user: MyUser = await sync_to_async(
            MyUser.objects.get)(discord_tag=str(ctx.author))
    except MyUser.DoesNotExist:
        await ctx.send(f"You're not registered.")

    msg = "Ignored Discord users: "
    async for ignored_tag in list_muncher(
            await sync_to_async(list)(db_user.discord_ignored_users)):
        msg += f"{ignored_tag}, "
    # If user has no ignores.
    if msg == "Ignored Discord users: ":
        await ctx.send("No ignores.")
    else:
        await ctx.send(msg[:-2])


async def list_muncher(lst: list):
    """Helper function to consume lists in async-for."""

    lst2 = lst.copy()
    while lst2:
        yield lst2.pop(0)


# TODO: Test with unregistered user.
@client.command(name="enable")
async def enable(ctx):
    guild = ctx.guild
    author = ctx.author
    # Check if guild exists.
    try:
        db_guild = await sync_to_async(Guild.objects.get)(
            guild_id=str(guild.id)
        )
    # If it doesn't, create it.
    except Guild.DoesNotExist as _:
        db_guild = await sync_to_async(Guild.objects.create)(
            guild_id=str(guild.id),
            guild_name=guild.name
        )
        db_guild.save()
    # Check that message author is registered (their tag is in database).
    try:
        db_author = await sync_to_async(MyUser.objects.get)(
            discord_tag=str(author)
        )
        # Succeeds fine if author already has enabled this guild.
        try:
            _ = await sync_to_async(db_author.discord_enabled_guilds.get)(
                guild_id=str(guild.id)
            )
            await ctx.send("Already enabled.")
            return
        except Guild.DoesNotExist as _:
            await sync_to_async(db_author.discord_enabled_guilds.add)(db_guild)
            await ctx.send(f"Done. You have enabled effects on {guild.name}.")
            return
    except MyUser.DoesNotExist as _:
        await ctx.send("You have not registered.")
        return


@client.command(name="disable")
async def disable(ctx):
    guild = ctx.guild
    author = ctx.author
    # First try if guild is in DB. (Someone has or has had it enabled.)
    try:
        db_guild = await sync_to_async(Guild.objects.get)(guild_id=guild.id)
    except Guild.DoesNotExist as e:
        await ctx.send(
            "You hadn't this guild enabled to begin with. In fact, no one has."
        )
        return
    # If user is in DB, disable notifications for this guild.
    try:
        db_author = await sync_to_async(MyUser.objects.get)(
            discord_tag=str(author)
        )
        # OK, so user is in DB, since no exception. Check whether the guild
        # is enabled or disabled.
        try:
            await sync_to_async(db_author.discord_enabled_guilds.get)(
                guild_id=str(guild.id))
            # No exception, so user has the guild enabled. Disable it.
            await sync_to_async(db_author.discord_enabled_guilds.remove)(
                db_guild)
            await ctx.send(
                f"Done. You have disabled light notifications on {guild.name}."
            )
        except Guild.DoesNotExist as _:
            await ctx.send(
                f"You already have notifications on {guild.name} disabled.")
    except MyUser.DoesNotExist as e:
        await ctx.send(f"You have to register first to do anything.")


async def do_effects(bulb: LIFXLight, user: MyUser):
    """Do light effects on given bulb."""

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
    """Get discord-enabled bulbs of user."""

    ret = []
    for bulb in user.lifxlight_set.all():
        if bulb.discord_enabled:
            ret.append(bulb)
    return ret


client.run(os.getenv("DISCORD_BOT_TOKEN"))
