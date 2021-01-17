import math
import random
from typing import Optional

import discord
from bot.constants import Channels, Colours, ERROR_REPLIES, NEGATIVE_REPLIES
from discord import Embed, Message
from discord.ext import commands
from loguru import logger


class CommandErrorHandler(commands.Cog):
    """Handles errors emitted from commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def revert_cooldown_counter(command: commands.Command, message: Message) -> None:
        """Undoes the last cooldown counter for user-error cases."""
        if command._buckets.valid:
            bucket = command._buckets.get_bucket(message)
            bucket._tokens = min(bucket.rate, bucket._tokens + 1)
            logger.debug(
                "Cooldown counter reverted as the command was not used correctly."
            )

    @staticmethod
    def error_embed(message: str, title: Optional[str] = None) -> Embed:
        """Build a basic embed with red colour and either a random error title or a title provided."""
        title = title or random.choice(ERROR_REPLIES)
        embed = Embed(colour=Colours.soft_red, title=title)
        embed.description = message
        return embed

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Activates when a command opens an error."""
        if getattr(error, "handled", False):
            logger.debug(
                f"Command {ctx.command} had its error already handled locally; ignoring."
            )
            return

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return  # Skip logging CommandNotFound Error

        elif isinstance(error, commands.UserInputError):
            if isinstance(error, commands.MissingRequiredArgument):
                description = (
                    f"`{error.param.name}` is a required argument that is missing."
                    "\n\nUsage:\n"
                    f"```{ctx.prefix}{ctx.command} {ctx.command.signature}```"
                )
            else:
                description = (
                    f"Your input was invalid: {error}\n\nUsage:\n"
                    f"```{ctx.prefix}{ctx.command} {ctx.command.signature}```"
                )

            embed = self.error_embed(description)
            await ctx.send(embed=embed)

        elif isinstance(error, commands.CommandOnCooldown):
            mins, secs = divmod(math.ceil(error.retry_after), 60)
            embed = self.error_embed(
                f"This command is on cooldown:\nPlease retry in **{mins} minutes {secs} seconds**.",
                NEGATIVE_REPLIES,
            )
            await ctx.send(embed=embed, delete_after=10)

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(
                embed=self.error_embed(
                    "This command has been disabled.", NEGATIVE_REPLIES
                )
            )

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                embed=self.error_embed(
                    "This command can only be used in the server.", NEGATIVE_REPLIES
                )
            )

        elif isinstance(error, commands.BadArgument):
            self.revert_cooldown_counter(ctx.command, ctx.message)
            embed = self.error_embed(
                "The argument you provided was invalid: "
                f"{error}\n\nUsage:\n```{ctx.prefix}{ctx.command} {ctx.command.signature}```"
            )
            await ctx.send(embed=embed)
        else:
            await self.handle_unexpected_error(ctx, error)
            return  # Exit early to avoid logging.

        logger.debug(
            f"Error Encountered: {type(error).__name__} - {str(error)}, "
            f"Command: {ctx.command}, "
            f"Author: {ctx.author}, "
            f"Channel: {ctx.channel}"
        )

    async def handle_unexpected_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Send a generic error message in `ctx` and log the exception as an error with exc_info."""
        await ctx.send(
            f"Sorry, an unexpected error occurred. Please let us know!\n\n"
            f"```{error.__class__.__name__}: {error}```"
        )

        push_alert = Embed(
            title="An unexpected error occurred",
            color=Colours.soft_red,
        )
        push_alert.add_field(
            name="User",
            value=f"id: {ctx.author.id} | username: {ctx.author.mention}",
            inline=False,
        )
        push_alert.add_field(
            name="Command", value=ctx.command.qualified_name, inline=False
        )
        push_alert.add_field(
            name="Message & Channel",
            value=f"Message: [{ctx.message.id}]({ctx.message.jump_url}) | Channel: <#{ctx.channel.id}>",
            inline=False,
        )
        push_alert.add_field(
            name="Full Message", value=ctx.message.content, inline=False
        )

        dev_alerts = self.bot.get_channel(Channels.devalerts)
        if dev_alerts is None:
            logger.info(
                f"Fetching dev-alerts channel as it wasn't found in the cache (ID: {Channels.devalerts})"
            )
            try:
                dev_alerts = await self.bot.fetch_channel(Channels.devalerts)
            except discord.HTTPException as discord_exc:
                logger.exception("Fetch failed", exc_info=discord_exc)
                return

        await dev_alerts.send(embed=push_alert)
        logger.error(
            f"Error executing command invoked by {ctx.message.author}: {ctx.message.content}",
            exc_info=error,
        )


def setup(bot: commands.Bot) -> None:
    """Error handler Cog load."""
    bot.add_cog(CommandErrorHandler(bot))
