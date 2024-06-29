from datetime import datetime, timedelta
from typing import Any

import discord
import pytz
from config import get_config
from discord import app_commands
from discord.flags import Intents
from dpn_pyutils.common import get_logger
from summariser.client import SummariserClient

log = get_logger(__name__)

config = get_config()


class DiscordBotClient(discord.Client):
    """
    Wrapper class for a Discord Bot to speed up command sync
    """

    tree: app_commands.CommandTree

    moderator_channel: discord.TextChannel

    summariser: SummariserClient

    def __init__(self, *, intents: Intents, **options: Any) -> None:
        """
        Initialize the bot and sync it to a specific guild, so that we don't have to
        wait for commands to sync
        """
        super().__init__(intents=intents, **options)
        self.tree = app_commands.CommandTree(self)
        self.summariser = SummariserClient()

    async def setup_hook(self):
        self.tree.copy_global_to(guild=discord.Object(id=config.DISCORD_BOT_GUILD_ID))
        await self.tree.sync(guild=discord.Object(id=config.DISCORD_BOT_GUILD_ID))

    async def hydrate_summariser(self):
        """
        Hydrates the summarizer with a range of content
        """

        message_threshold_dt = datetime.now(tz=pytz.UTC) - timedelta(
            seconds=config.SUMMARISER_MESSAGE_AGE_THRESHOLD
        )
        guild = self.get_guild(config.DISCORD_BOT_GUILD_ID)
        if guild is None:
            raise RuntimeError(
                f"Could not find guild with ID {config.DISCORD_BOT_GUILD_ID}"
            )

        for category in guild.categories:
            if category.id not in config.DISCORD_BOT_CATEGORY_IDS:
                continue

            log.info(
                "Checking configured category (%s) #%s", category.id, category.name
            )
            for channel in category.channels:
                log.info(
                    "Hydrating summariser with messages from channel #%s", channel.name
                )
                await self.summariser.hydrate_messages_channel(channel, message_threshold_dt)  # type: ignore

            log.info("All configured channels have been hydrated.")
