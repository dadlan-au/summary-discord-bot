from datetime import datetime, timedelta
from typing import List

import discord
import humanize
import pytz
from config import get_config
from dpn_pyutils.common import get_logger

log = get_logger(__name__)

config = get_config()


class PrunerClient:

    message_threshold_offset: int

    autopruned_channels: List[int]

    ignored_messages: List[int]

    def __init__(self):
        """
        Initializes the pruner
        """

        self.message_threshold_offset = config.PRUNER_MESSAGE_AGE_THRESHOLD
        self.autopruned_channels = config.PRUNER_AUTOPRUNE_CHANNELS
        self.ignored_messages = config.PRUNER_IGNORE_MESSAGES

    async def prune(self, guild: discord.Guild):
        """
        Prunes the messages in the configured channels
        """

        message_threshold = datetime.now(tz=pytz.UTC) - timedelta(
            seconds=self.message_threshold_offset
        )

        mod_channel = guild.get_channel(config.PRUNER_MOD_CHANNEL)
        if mod_channel is None:
            raise ValueError(
                f"Could not find mod notification channel with ID #{config.PRUNER_MOD_CHANNEL} "
                "(PRUNER_MOD_CHANNEL)"
            )

        for channel_id in self.autopruned_channels:
            channel = guild.get_channel(channel_id)
            if channel is None:
                log.warn("Could not find channel with ID %s", channel_id)
                continue

            try:
                if channel.type in [
                    discord.ChannelType.text,
                    discord.ChannelType.news,
                    discord.ChannelType.news_thread,
                    discord.ChannelType.forum,
                    discord.ChannelType.public_thread,
                ]:
                    messages_pruned = await self.prune_channel(channel, message_threshold)  # type: ignore
                    relative_time_string = humanize.naturaltime(message_threshold)
                    threshold_time_string = message_threshold.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if messages_pruned > 0:
                        mod_notification = discord.Embed(
                            title=f"Auto Prune summary for #{channel.name} ({channel.id})",
                            description=(
                                f"Pruned {messages_pruned} messages older than {relative_time_string} ( {threshold_time_string} UTC ) "
                                f"from channel #{channel.jump_url}"
                            ),
                        )

                        await mod_channel.send(embed=mod_notification)  # type: ignore
                else:
                    log.warn(
                        "Channel #%s (%s) is not a message-based channel, skipping pruning",
                        channel.name,
                        channel.id,
                    )
            except discord.errors.Forbidden as e:
                log.error(
                    "Could not delete messages in channel #%s (%s) due to lack of permissions. Ensure the "
                    "bot has Manage Messages permissions in this channel",
                    channel.name,
                    channel.id,
                )

                mod_notification = discord.Embed(
                    title=f"Could not delete messages in channel #{channel.name}",
                    description=(
                        f"Could not delete messages in #{channel.name}:\n `{e}` \n\n"
                        f"Make sure the bot has **Manage Messages permission** in this channel."
                    ),
                )

                await mod_channel.send(embed=mod_notification)  # type: ignore
            except discord.errors.DiscordServerError as e:
                log.error("Discord server error: %s", e)
                pass

    async def prune_channel(
        self,
        channel: discord.ForumChannel | discord.TextChannel | discord.Thread,
        message_threshold: datetime,
    ) -> int:
        """
        Prunes messages older than a certain threshold in a channel
        """

        log.info(
            "Auto-pruning messages in channel #%s (%s) older than %s",
            channel.name,
            channel.id,  # type: ignore
            message_threshold,
        )

        messages_pruned = 0

        if channel.type in [
            discord.ChannelType.text,
            discord.ChannelType.news,
            discord.ChannelType.news_thread,
            discord.ChannelType.public_thread,
        ]:
            async for message in channel.history(limit=None, before=message_threshold):  # type: ignore
                if message.id in self.ignored_messages:
                    log.debug(
                        "Skipping ignored message #%s at %s by %s",
                        message.id,
                        message.created_at,
                        message.author,
                    )
                    continue

                log.info(
                    "Pruning message #%s at %s by %s",
                    message.id,
                    message.created_at,
                    message.author,
                )
                await message.delete()
                messages_pruned += 1

        elif channel.type == discord.ChannelType.forum:
            for thread in channel.threads:
                async for message in thread.history(
                    limit=None, before=message_threshold
                ):
                    if message.id in self.ignored_messages:
                        log.debug(
                            "Skipping ignored message #%s at %s by %s",
                            message.id,
                            message.created_at,
                            message.author,
                        )
                        continue

                    log.info(
                        "Pruning message #%s at %s by %s",
                        message.id,
                        message.created_at,
                        message.author,
                    )
                    await message.delete()
                    messages_pruned += 1

        else:
            log.warn(
                "Channel #%s (%s) is not a message-based channel, skipping pruning",
                channel.name,
                channel.id,
            )

        return messages_pruned
