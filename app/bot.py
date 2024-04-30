from datetime import datetime, time, timedelta
from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo

import discord
import pytz
from config import AppSettings
from discord.errors import Forbidden
from discord.ext import tasks
from dpn_pyutils.common import get_logger
from render import render_template

log = get_logger(__name__)


async def get_text_channel(
    client: discord.Client, channel_id: int
) -> discord.TextChannel:
    """
    Get the text channel object from the client
    """

    return await client.fetch_channel(channel_id)  # type: ignore


def get_active_since_datetime() -> datetime:
    """
    Get the active since datetime
    """
    current_dateTime = datetime.now()
    day_ago = current_dateTime.replace(tzinfo=None) - timedelta(hours=24)

    return day_ago


async def get_active_channels(client: discord.Client) -> List:
    """
    Gets the active channels
    """

    day_ago = get_active_since_datetime()
    log.debug("Getting active channels since %s", day_ago)
    channels = []

    # Loop through all the guilds the client is connected to - there should only be one
    for guild in client.guilds:
        log.debug("Checking guild: %s", guild.name)

        # Loop through all the text channels on the server
        for channel in guild.text_channels:
            log.debug("Checking channel (%s) %s", channel.id, channel.name)
            try:
                if channel.last_message_id is not None:
                    last_message = await channel.fetch_message(channel.last_message_id)
                    last_message_date = last_message.created_at
                    if last_message_date.replace(
                        tzinfo=ZoneInfo("UTC")
                    ) > day_ago.replace(tzinfo=ZoneInfo("UTC")):
                        channels.append(channel)
            except Forbidden as e:
                log.warn("Access to channel %s is forbidden: %s", channel.name, e)
                pass
            except Exception as e:
                log.error(
                    "Error with last message in that thread: %s (type: %s)",
                    e,
                    type(e),
                )

    return channels


async def get_active_threads(client: discord.Client) -> List:
    """
    Gets the active threads
    """

    day_ago = get_active_since_datetime()
    log.debug("Getting active threads since %s", day_ago)
    threads = []

    # Loop through all the guilds the client is connected to - there should only be one
    for guild in client.guilds:
        log.debug("Checking guild: %s", guild.name)

        for forum in guild.forums:
            log.debug("Checking forum %s", forum.name)

            for thread in forum.threads:
                log.debug("Checking thread %s", thread.name)
                try:
                    if thread.last_message_id is not None:
                        last_thread_message = await thread.fetch_message(
                            thread.last_message_id
                        )
                        last_thread_message_date = last_thread_message.created_at

                        if last_thread_message_date.replace(
                            tzinfo=pytz.UTC
                        ) > day_ago.replace(tzinfo=pytz.UTC):
                            threads.append(thread)
                except Forbidden:
                    pass
                except Exception as e:
                    log.error(
                        "Error with last message in that thread: %s (type: %s)",
                        e,
                        type(e),
                    )

    return threads


def create_bot(config: AppSettings) -> discord.Client:
    """
    Creates the discord bot and ensures that it is configured appropriately
    """

    configured_tz = ZoneInfo(config.TIMEZONE)
    log.debug("Configured timezone: %s", configured_tz)

    post_hour = int(config.SUMMARY_POST_AT_LOCALTIME.split(":")[0])
    post_minute = int(config.SUMMARY_POST_AT_LOCALTIME.split(":")[1])
    run_at_time = time(hour=post_hour, minute=post_minute, tzinfo=configured_tz)

    log.debug(
        "Will be running at %s (%s) every day",
        run_at_time,
        run_at_time.tzinfo,
    )

    # return

    # Declare intents
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    # On Ready - On bot run - start the daily loop.
    @client.event
    async def on_ready():
        log.info("Discord user connected as '%s'", client.user)
        announce_channel = await get_text_channel(
            client, config.DISCORD_POST_MESSAGE_CHANNEL
        )

        log.debug(
            "Announcing to channel #%s (%s)", announce_channel.name, announce_channel.id
        )
        daily_channel_message_count.start()

    # Function to run daily at a specific time
    @tasks.loop(time=run_at_time)
    async def daily_channel_message_count(announce_channel_id: int | None = None):

        log.info(
            "Running daily_channel_message_count at %s", datetime.now(configured_tz)
        )

        if announce_channel_id is None:
            announce_channel_id = config.DISCORD_POST_MESSAGE_CHANNEL

        announce_channel = await get_text_channel(client, announce_channel_id)
        if announce_channel is None:
            log.warn(
                "Could not find channel '%s' and hence cannot send announcement.",
                config.DISCORD_POST_MESSAGE_CHANNEL,
            )
            return

        # Valid announcement channel exists, proceed with gathering data and rendering the announcement
        channels = await get_active_channels(client)
        threads = await get_active_threads(client)

        log.debug(
            "Sending announcement to channel #%s (%s)",
            announce_channel.name,
            announce_channel.id,
        )
        # Render the template
        announcement = render_template(
            Path(config.RENDER_TEMPLATE_FILE), channels, threads
        )

        await announce_channel.send(announcement)

    # Command to inform when it will happen
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if str(message.content).strip() == "$activity":
            # Reply in the channel that the message was posted
            await daily_channel_message_count(message.channel.id)

    return client








































