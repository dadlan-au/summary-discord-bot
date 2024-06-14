from datetime import datetime, timedelta
from typing import List, Tuple
from zoneinfo import ZoneInfo

import discord
import pytz
from config import get_config
from discord.errors import Forbidden
from dpn_pyutils.common import get_logger

log = get_logger(__name__)

config = get_config()


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


async def get_active_channels_and_threads(client: discord.Client) -> Tuple[List, List]:
    """
    Gets the active channels
    """

    day_ago = get_active_since_datetime()
    log.debug("Getting active channels and threads since %s", day_ago)
    channels = []
    threads = []

    log.debug("Active categories to check: %s", config.DISCORD_BOT_CATEGORY_IDS)

    # Loop through all the guilds the client is connected to - there should only be one
    for guild in client.guilds:
        if guild.id != config.DISCORD_BOT_GUILD_ID:
            continue

        log.debug("Checking guild: %s", guild.name)
        for category in guild.categories:
            if category.id not in config.DISCORD_BOT_CATEGORY_IDS:
                continue

            log.debug(
                "Checking configured category (%s) %s", category.id, category.name
            )
            for channel in category.channels:

                log.debug("Checking channel (%s) %s", channel.id, channel.name)
                try:

                    if channel.type == discord.ChannelType.text:
                        last_message = await channel.fetch_message(
                            channel.last_message_id # type: ignore
                        )
                        last_message_date = last_message.created_at
                        if last_message_date.replace(
                            tzinfo=ZoneInfo("UTC")
                        ) > day_ago.replace(tzinfo=ZoneInfo("UTC")):
                            channels.append(channel)

                    if (
                        channel.type == discord.ChannelType.text
                        or channel.type == discord.ChannelType.forum
                        and channel.last_message_id is not None
                    ):
                        for thread in channel.threads:
                            log.debug("Checking thread (%s) %s", thread.id, thread.name)
                            if thread.last_message_id is not None:
                                last_thread_message = await thread.fetch_message(
                                    thread.last_message_id
                                )
                                last_thread_message_date = (
                                    last_thread_message.created_at
                                )

                                if last_thread_message_date.replace(
                                    tzinfo=pytz.UTC
                                ) > day_ago.replace(tzinfo=pytz.UTC):
                                    threads.append(thread)

                except Forbidden as e:
                    log.warn("Access to channel %s is forbidden: %s", channel.name, e)
                    pass
                except Exception as e:
                    log.error(
                        "Error with last message in that thread: %s (type: %s)",
                        e,
                        type(e),
                    )

    return channels, threads

