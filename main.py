import discord
import os

from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone, time
from discord.ext import tasks

# Set the time of day for the message count to run.
utc = timezone.utc
# run_at_time = time(hour=10, minute=0, tzinfo=utc)
run_at_time = time(hour=12, minute=21, tzinfo=utc)

# Retrieve Discord App Token from environment variable
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Declare intents
intents=discord.Intents.default()
intents.message_content = True

# Create Discord Client
client = discord.Client(intents=intents)

# On Ready - On bot run - start the daily loop.
@client.event
async def on_ready():

    print(
        f'{client.user} is connected'
    )

    daily_channel_message_count.start()


# Function to run daily at a specific time
@tasks.loop(time=run_at_time)
async def daily_channel_message_count():
        
    # current datetime and day ago is the time now and 24 hours prior.
    current_dateTime = datetime.now()
    day_ago = current_dateTime.replace(tzinfo=None) - timedelta(hours=24)

    # Variable to store the general channel object
    general_channel = 0

    # Message string for announcement
    announcement = """**Daily Activity**\n\nChannels:\n\n"""

    # Loop through all the guilds the client is connected to.
    for guild in client.guilds:

        # Loop through all the text channels on the server
        for channel in guild.text_channels:

            # If the channel is the general channel then store it for use.
            if channel.name == 'general':
                general_channel = channel

            # Reset the counter
            message_count = 0

            # Get the channel message history
            messages = [message async for message in channel.history(limit=1)]

            # Loop through messages
            for msg in messages:

                # Add message if occurred in the last 24 hours
                if msg.created_at.replace(tzinfo=utc) > day_ago.replace(tzinfo=utc):
                    message_count += 1

                # Stop if occurred over 24 hours ago
                if msg.created_at.replace(tzinfo=utc) < day_ago.replace(tzinfo=utc):
                    break
            
            if message_count > 0:
                announcement += channel.jump_url +"\n\n"

        announcement += """\n\nForum Threads:\n\n"""
        
        for forum in guild.forums:
            for thread in forum.threads:
                messages = [message async for message in thread.history(limit=1)]

                message_thread_count = 0

                for msg in messages:

                    # Add message if occurred in the last 24 hours
                    if msg.created_at.replace(tzinfo=utc) > day_ago.replace(tzinfo=utc):
                        message_thread_count += 1

                    # Stop if occurred over 24 hours ago
                    if msg.created_at.replace(tzinfo=utc) < day_ago.replace(tzinfo=utc):
                        break

                if message_thread_count > 0:
                    announcement += thread.jump_url +"\n\n"

        announcement += "24 hour period from 9pm yesterday to 9pm today."

            # Send to general chat
        await general_channel.send(announcement)

client.run(TOKEN)