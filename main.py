import os
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import List

import discord
import pytz
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
from dpn_pyutils.file import read_file_text
from jinja2 import BaseLoader, Environment

# Set the time of day for the message count to run.
utc = timezone.utc

run_at_time = time(hour=10, minute=0, tzinfo=utc)

# Retrieve Discord App Token from environment variable
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

eastern_tz = pytz.timezone("Australia/Sydney")
hrs_diff = int(
    datetime.now(pytz.timezone("Australia/Sydney"))
    .strftime("%z")
    .split("00")[0]
    .split("+")[1]
)

# Declare intents
intents = discord.Intents.all()

# Create Discord Client
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# On Ready - On bot run - start the daily loop.
@client.event
async def on_ready():
    print(f"{client.user} is connected")

    daily_channel_message_count.start()

# Function to run daily at a specific time
@tasks.loop(time=run_at_time)
async def daily_channel_message_count():
    current_dateTime = datetime.now()
    day_ago = current_dateTime.replace(tzinfo=None) - timedelta(hours=24)

    # Variable to store the general channel object
    general_channel = None

    channels = []
    threads = []

    # Loop through all the guilds the client is connected to.
    for guild in client.guilds:
        # Loop through all the text channels on the server
        for channel in guild.text_channels:
            # If the channel is the general channel then store it for use.
            if channel.name == "general":
                general_channel = channel

            try:
                if channel.last_message_id is not None:
                    last_message = await channel.fetch_message(channel.last_message_id)
                    last_message_date = last_message.created_at
                    if last_message_date.replace(tzinfo=utc) > day_ago.replace(
                        tzinfo=utc
                    ):
                        channels.append(channel)

            except Exception as e:
                print(f"Error with last message in that thread: {e} (type: {type(e)}))")

        for forum in guild.forums:
            for thread in forum.threads:
                try:
                    if thread.last_message_id is not None:
                        last_thread_message = await thread.fetch_message(
                            thread.last_message_id
                        )
                        last_thread_message_date = last_thread_message.created_at

                        if last_thread_message_date.replace(
                            tzinfo=utc
                        ) > day_ago.replace(tzinfo=utc):
                            threads.append(thread)
                except Exception as e:
                    print(
                        f"Error with last message in that thread: {e} (type: {type(e)}))"
                    )

        announcement = render_template(channels, threads)

        # Send to general chat if we have found one
        if general_channel is not None:
            await general_channel.send(announcement)
        else:
            print("No general channel found")


# Command to inform when it will happen
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == "$activity" and message.channel.name == "general":
        # await message.channel.send("I go off at "+str((datetime.combine(date.today(), run_at_time) + timedelta(hours=hrs_diff)).strftime("%H:%M:%S %d/%m/%Y")))
        await daily_channel_message_count()


def render_template(channels: List, threads: List) -> str:
    """
    Renders a list of channels and threads into a template
    """

    environment = Environment(loader=BaseLoader(), autoescape=True)

    tpl = environment.from_string(
        read_file_text(Path("template.jinja2")),
        globals={"channels": channels, "threads": threads},
    )

    return tpl.render()


# Run the bot
if TOKEN is None:
    raise ValueError("No token found in environment variables.")

client.run(TOKEN)
