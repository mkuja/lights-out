WHAT IS THIS?
=============

This repo is a Discord bot and a related Django site. The bot gives light notifications
using LIFX smart lights when the user is being mentioned in Discord. Unfortunate is
LIFX wants only select partners to access to their authentication thing, and thus users
of this bot have to get their own LIFX developer token.


BOT SETUP
==========

To run the bot you need to set up a bot account for Discord with permissions
to send text messages and read message history. To run the bot add the following
in your .env file:

DISCORD_BOT_TOKEN = "your_token"


DATABASE
========

To have the database code work you must use PostgreSQL. Unless you are using
identd to authenticate, you must set your credentials in addition to
DB connection in the .env file:

POSTGRES_USER = "your_user"
POSTGRES_PASSWORD = "your_password"
POSTGRES_HOST = "127.0.0.1"
POSTGRES_DB_NAME = "lights_out"
POSTGRES_PORT = 5432


DJANGO DEVELOPMENT SERVER
=========================

To run django development server you must set DJANGO_SETTINGS_MODULE environment
variable. In project root type:

export DJANGO_SETTINGS_MODULE=discord_bot_website.settings
python manage.py runserver 8000


You can make a Django admin account to access http://localhost:8000/admin using:

python manage.py createsuperuser


If you want flashing lights and stuff, you need to set your LIFX-token on the
website.


DEPLOYMENT
===========

Sorry, I don't want to write too long. If you are really interested, you can
ask Felixi#4661 on https://discord.gg/eKtHWFbrGT or google how to deploy a
django project and how to make a systemd service, make a hole in your
firewall, etc. I think there are many ways to go about it, and I for sure only
know how to do it on Ubuntu/Fedora.
