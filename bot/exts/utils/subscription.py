import discord
from bot.bot import Bot
from bot.constants import ANNOUNCEMENTS_ID, Emojis, POLLS_ID
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog, Context

color = 0x32A05A


class Subscription(Cog):
    """Subscribing and Unsubscrbing to announcements and polls notifications."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.group(name="subscribe", invoke_without_command=True)
    async def subscribe_group(self, ctx: Context) -> None:
        """Subscribe to announcements and polls notifications by assigning yourself the role."""
        has_announcements = False
        has_polls = False
        for role in ctx.author.roles:
            if role.id == ANNOUNCEMENTS_ID:
                has_announcements = True
            if role.id == POLLS_ID:
                has_polls = True
        if has_announcements and has_polls:
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already subscribed",
                description=f"You're already subscribed to {ctx.guild}'s announcements and polls.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)
            return

        elif has_polls:
            await ctx.author.add_roles(
                discord.Object(ANNOUNCEMENTS_ID),
                reason="Subscribed to announcements",
            )
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} Subscribed",
                description=f"You've subscribed to {ctx.guild}'s announcements.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        elif has_announcements:
            await ctx.author.add_roles(
                discord.Object(POLLS_ID),
                reason="Subscribed to polls",
            )
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} Subscribed",
                description=f"You've subscribed to {ctx.guild}'s polls.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        else:
            await ctx.author.add_roles(
                discord.Object(ANNOUNCEMENTS_ID),
                reason="Subscribed to announcements",
            )
            await ctx.author.add_roles(
                discord.Object(POLLS_ID), reason="Subscribed to polls"
            )
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} Subscribed",
                description=f"You've subscribed to {ctx.guild}'s announcements and polls.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

    @commands.group(name="unsubscribe", invoke_without_command=True)
    async def unsubscribe_group(self, ctx: Context) -> None:
        """Unsubscribe to announcements and polls notifications by assigning yourself the role."""
        has_announcements = False
        has_polls = False
        for role in ctx.author.roles:
            if role.id == ANNOUNCEMENTS_ID:
                has_announcements = True
            if role.id == POLLS_ID:
                has_polls = True
        if has_announcements and has_polls:
            await ctx.author.remove_roles(
                discord.Object(ANNOUNCEMENTS_ID),
                reason="Unsubscribed to announcements",
            )
            await ctx.author.remove_roles(
                discord.Object(POLLS_ID), reason="Unsubscribed to polls"
            )
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} Unsubscribed",
                description=f"You've unsubscribed to {ctx.guild}'s announcements and polls.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        elif has_polls:
            await ctx.author.remove_roles(
                discord.Object(POLLS_ID), reason="Unsubscribed to polls"
            )
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} Unsubscribed",
                description=f"You've unsubscribed to {ctx.guild}'s polls.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        elif has_announcements:
            await ctx.author.remove_roles(
                discord.Object(ANNOUNCEMENTS_ID),
                reason="Unsubscribed to announcements",
            )
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} Unsubscribed",
                description=f"You've unsubscribed to {ctx.guild}'s announcements.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        else:
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already unsubscribed",
                description=f"You're already unsubscribed to {ctx.guild}'s announcements and polls.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

    @subscribe_group.command(name="announcements", aliases=("announcement",))
    async def announcements_subscribe(self, ctx: Context, *_) -> None:
        """Subscribe to announcements by assigning yourself the role."""
        for role in ctx.author.roles:
            if role.id == ANNOUNCEMENTS_ID:
                embed = Embed(
                    title=f"{Emojis.warning_emoji} Already subscribed",
                    description=f"You're already subscribed to {ctx.guild}'s announcements.",
                    color=color,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
                return
        await ctx.author.add_roles(
            discord.Object(ANNOUNCEMENTS_ID), reason="Subscribed to announcements"
        )
        embed = Embed(
            title=f"{Emojis.confirmation_emoji} Subscribed",
            description=f"You've subscribed to {ctx.guild}'s announcements.",
            color=color,
        )
        await ctx.send(content=ctx.author.mention, embed=embed)

    @unsubscribe_group.command(name="announcements", aliases=("announcement",))
    async def announcements_unsubscribe(self, ctx: Context, *_) -> None:
        """Unsubscribe to announcements by unassigning yourself the role."""
        has_role = False
        for role in ctx.author.roles:
            if role.id == ANNOUNCEMENTS_ID:
                has_role = True
                break
        if not has_role:
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already unsubscribed",
                description=f"You're already unsubscribed to {ctx.guild}'s announcements.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)
            return
        await ctx.author.remove_roles(
            discord.Object(ANNOUNCEMENTS_ID), reason="Unsubscribed to announcements"
        )
        embed = Embed(
            title=f"{Emojis.confirmation_emoji} Unsubscribed",
            description=f"You've unsubscribed to {ctx.guild}'s announcements.",
            color=color,
        )
        await ctx.send(content=ctx.author.mention, embed=embed)

    @subscribe_group.command(name="polls", aliases=("poll",))
    async def polls_subscribe(self, ctx: Context, *_) -> None:
        """Subscribe to polls by assigning yourself the role."""
        for role in ctx.author.roles:
            if role.id == POLLS_ID:
                embed = Embed(
                    title=f"{Emojis.warning_emoji} Already subscribed",
                    description=f"You're already subscribed to {ctx.guild}'s polls.",
                    color=color,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
                return
        await ctx.author.add_roles(
            discord.Object(POLLS_ID), reason="Subscribed to polls"
        )
        embed = Embed(
            title=f"{Emojis.confirmation_emoji} Subscribed",
            description=f"You've subscribed to {ctx.guild}'s polls.",
            color=color,
        )
        await ctx.send(content=ctx.author.mention, embed=embed)

    @unsubscribe_group.command(name="polls", aliases=("poll",))
    async def polls_unsubscribe(self, ctx: Context, *_) -> None:
        """Unsubscribe to polls by unassigning yourself the role."""
        has_role = False
        for role in ctx.author.roles:
            if role.id == POLLS_ID:
                has_role = True
                break
        if not has_role:
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already unsubscribed",
                description=f"You're already unsubscribed to {ctx.guild}'s polls.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)
            return
        await ctx.author.remove_roles(
            discord.Object(POLLS_ID), reason="Unsubscribed to polls"
        )
        embed = Embed(
            title=f"{Emojis.confirmation_emoji} Unsubscribed",
            description=f"You've unsubscribed to {ctx.guild}'s polls.",
            color=color,
        )
        await ctx.send(content=ctx.author.mention, embed=embed)


def setup(bot: Bot) -> None:
    """Load the Subscription cog."""
    bot.add_cog(Subscription(bot))
