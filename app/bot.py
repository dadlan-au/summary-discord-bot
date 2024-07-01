import uuid
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import discord
from channels.scanner import get_active_channels_and_threads, get_text_channel
from config import AppSettings, get_config
from discord import app_commands
from discord.ext import tasks
from discord.message import Message
from discordbot import DiscordBotClient
from dpn_pyutils.common import get_logger
from humanitix.client import HumanitixClient
from humanitix.summary import create_summary_from_event_data
from render import render_template, split_rendered_text_max_length
from rendering.graphic import create_image_tix, create_text_tix

log = get_logger(__name__)

config = get_config()


async def raise_discord_error(ctx, e):
    error_uuid = uuid.uuid4()
    log.error("Error invoking command: %s \n ctx = %s uuid = %s", e, ctx, error_uuid)
    await ctx.followup.send(  # type: ignore
        "An error occurred while processing your request. Please raise a helpdesk ticket and "
        f"paste the following error code: {error_uuid}"
    )
    log.error("All responses sent, error handled")


def create_bot(config: AppSettings) -> DiscordBotClient:
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

    # Declare intents
    intents = discord.Intents.default()
    intents.message_content = True
    client = DiscordBotClient(intents=intents)

    # On Ready - On bot run - start the daily loop.
    @client.event
    async def on_ready():
        log.info("Discord user connected as '%s'", client.user)
        announce_channel = await get_text_channel(
            client, config.DISCORD_POST_MESSAGE_CHANNEL
        )

        await client.hydrate_summariser()
        log.debug(
            "Announcing to channel #%s (%s)", announce_channel.name, announce_channel.id
        )
        daily_channel_message_count.start()
        cron_prune_summarizer.start()

        if config.PRUNER_ENABLE:
            cron_pruner.start()

    @tasks.loop(seconds=config.PRUNER_PRUNE_INTERVAL)
    async def cron_pruner():
        """
        Runs the autoprune on the channels
        """

        log.debug("Running autoprune on channels")
        guild = client.get_guild(config.DISCORD_BOT_GUILD_ID)
        if guild is None:
            log.error("Could not find guild with ID %s", config.DISCORD_BOT_GUILD_ID)
            return

        await client.pruner.prune(guild)

    @tasks.loop(seconds=config.SUMMARISER_PRUNE_INTERVAL)
    async def cron_prune_summarizer():
        """
        Runs a prune on the summarizer to ensure only relevant messages are stored
        """

        log.debug("Running prune on summarizer")
        client.summariser.prune()

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
        channels, threads = await get_active_channels_and_threads(client)

        log.debug(
            "Sending announcement to channel #%s (%s)",
            announce_channel.name,
            announce_channel.id,
        )
        # Render the template
        announcement = render_template(
            Path(config.RENDER_TEMPLATE_FILE), channels=channels, threads=threads
        )

        if (
            len(announcement) >= config.DISCORD_MAX_MESSAGE_LENGTH
            and config.SUMMARY_USE_MULTIPLE_MESSAGES
        ):
            messages = split_rendered_text_max_length(
                announcement, config.DISCORD_MAX_MESSAGE_LENGTH
            )
            for m in messages:
                await announce_channel.send(m)
        elif len(announcement) >= config.DISCORD_MAX_MESSAGE_LENGTH:
            await announce_channel.send(
                "Message too long for Discord and `SUMMARY_USE_MULTIPLE_MESSAGES = false`, "
                "cannot send the announcement to this channel."
            )
        else:
            await announce_channel.send(announcement)

    # Command to inform when it will happen
    @client.event
    async def on_message(message: Message):
        if message.author == client.user:
            return

        if str(message.content).strip() == "$activity":
            try:
                # Reply in the channel that the message was posted
                await daily_channel_message_count(message.channel.id)
            except discord.errors.DiscordException as e:
                await message.reply(f"An error occurred: {e}")

        client.summariser.record_message(message.channel.id, message)

    @client.event
    async def on_message_edit(before: Message, after: Message):
        """
        Records a message edit
        """

        client.summariser.update_message(after.channel.id, after.id, after)

    @client.event
    async def on_message_delete(message: Message):
        """
        Records a message deletion
        """

        client.summariser.delete_message(message.channel.id, message.id)

    @client.tree.command(
        name="activity",
        description="Gets the activity summary for the day since the configured time",
    )
    async def on_activity(
        ctx: discord.interactions.Interaction,
    ):
        """
        Gets the activity summary for the day
        """
        try:
            await ctx.response.defer(ephemeral=True, thinking=True)
            await daily_channel_message_count(ctx.channel_id)
            await ctx.followup.send("Activity summary sent", ephemeral=True)
        except discord.errors.DiscordException as e:
            await raise_discord_error(ctx, e)

    @client.tree.command(
        name="tix",
        description="Get the Humanitix data in graphical or text format for all or some of the subnets",
    )
    @app_commands.describe(
        subnet="The name (or part) of the subnet to find",
        format="The output method, valid options are 'image' or 'text'",
    )
    async def on_humanitix_graphics(
        ctx: discord.interactions.Interaction,
        subnet: str | None = None,
        format: str = "image",
    ):
        """
        Receives a graphics command
        """
        await humanitix_summary(ctx, subnet, format)

    @client.tree.command(
        name="tixt",
        description="Get the Humanitix data in text format for all or some of the subnets",
    )
    @app_commands.describe(
        subnet="The name (or part) of the subnet to find",
    )
    async def on_humanitix_text(
        ctx: discord.interactions.Interaction,
        subnet: str | None = None,
    ):
        """
        Receives a text command
        """
        await humanitix_summary(ctx, subnet, "text")

    @client.tree.command(
        name="digest",
        description="Generates a summary of the recent messages in this channel (up to 24h)",
    )
    @app_commands.describe(
        public="If True, the summary will be posted in the channel. If blank or False, it will be sent only to you"
    )
    async def on_digest_channel(
        ctx: discord.interactions.Interaction,
        public: bool = False,
    ):
        try:
            await client.summariser.generate_summary(ctx, public)
        except Exception as e:
            log.error("Error generating summary: %s", e)

    async def humanitix_summary(
        ctx: discord.interactions.Interaction,
        subnet: str | None = None,
        format: str = "image",
    ):
        """
        Performs the humanitix summary
        """

        try:
            log.debug("Received interaction from %s", ctx.user.name)
            await ctx.response.defer(ephemeral=False, thinking=True)

            if format is not None and format.lower() not in ["image", "text"]:
                await ctx.followup.send(
                    "Invalid format specified. Please use either 'image' or 'text'",
                    ephemeral=True,
                )
                return

            humanitix_client = HumanitixClient()
            events = await humanitix_client.filter_events_by_name(subnet)
            if events is None:
                message = "No events found"
                if subnet is not None:
                    message = f"No events found for '{subnet}'"

                await ctx.followup.send(message, ephemeral=True)
                return

            summary_data = await create_summary_from_event_data(events)
            if format.lower() == "text":
                formatted_message = create_text_tix(summary_data)
                await ctx.followup.send(formatted_message, ephemeral=False)
            else:
                image_path = create_image_tix(summary_data)
                await ctx.followup.send(
                    # "Here is the registrations summary",
                    ephemeral=False,
                    file=discord.File(image_path),
                )
                image_path.unlink()

        except discord.errors.DiscordException as e:
            await raise_discord_error(ctx, e)

    return client
