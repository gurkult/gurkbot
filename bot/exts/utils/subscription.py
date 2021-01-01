import discord
from bot.bot import Bot
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog, Context
from discord.utils import get

client = commands.Bot(command_prefix="a!")

yes_emoji = "<:yes:794231332770938901>"
no_emoji = "⚠️"
color = 0x32A05A

announcements_id = 793864455527202849
polls_id = 793864455527202848


class Subscription(Cog):
    """Subscribing and Unsubscrbing to announcements and polls notifications."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @client.command()
    async def subscribe(
        self, ctx: Context, announcements: str = None, polls: str = None
    ) -> None:
        """Subscribe to announcements and polls notifications by assigning yourself the role."""
        announcements_role = get(ctx.author.guild.roles, id=announcements_id)
        polls_role = get(ctx.author.guild.roles, id=polls_id)

        if announcements_role in ctx.author.roles and polls_role in ctx.author.roles:
            embed = Embed(
                title=f"{no_emoji} Already subscribed",
                description=f"You're already subscribed to {ctx.guild}'s announcements and polls.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)
            return

        elif not announcements and not polls:
            await ctx.author.add_roles(
                discord.Object(announcements_id), reason="Subscribed to announcements"
            )
            await ctx.author.add_roles(
                discord.Object(polls_id), reason="Subscribed to polls"
            )
            embed = Embed(
                title=f"{yes_emoji} Subscribed",
                description=f"You've subscribed to {ctx.guild}'s announcements and polls.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        elif announcements in ["announcements", "announcement"]:
            if announcements_role in ctx.author.roles:
                embed = Embed(
                    title=f"{no_emoji} Already subscribed",
                    description=f"You're already subscribed to {ctx.guild}'s announcements.",
                    color=color,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
            else:
                await ctx.author.add_roles(
                    discord.Object(announcements_id),
                    reason="Subscribed to announcements",
                )
                embed = Embed(
                    title=f"{yes_emoji} Subscribed",
                    description=f"You've subscribed to {ctx.guild}'s announcements.",
                    color=color,
                )
                embed = Embed(
                    title=f"{yes_emoji} Subscribed!",
                    description=f"You've subscribed to {ctx.guild}'s announcements.",
                    color=color,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)

        elif polls in ["polls", "poll"]:
            if polls_role in ctx.author.roles:
                embed = Embed(
                    title=f"{no_emoji} Already subscribed",
                    description=f"You're already subscribed to {ctx.guild}'s polls.",
                    color=color,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
            else:
                await ctx.author.add_roles(
                    discord.Object(polls_id), reason="Subscribed to polls"
                )
                embed = Embed(
                    title=f"{yes_emoji} Subscribed",
                    description=f"You've subscribed to {ctx.guild}'s polls.",
                    color=color,
                )
                embed = Embed(
                    title=f"{yes_emoji} subscribed",
                    description=f"You've subscribed to {ctx.guild}'s polls.",
                    color=color,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)

    @client.command()
    async def unsubscribe(
        self, ctx: Context, announcements: str = None, polls: str = None
    ) -> None:
        """Unsubscribe to announcements and polls notifications by unassigning yourself the role."""
        announcements_role = get(ctx.author.guild.roles, id=announcements_id)
        polls_role = get(ctx.author.guild.roles, id=polls_id)

        if (
            announcements_role not in ctx.author.roles
            and polls_role not in ctx.author.roles
        ):
            embed = Embed(
                title=f"{no_emoji} Already unsubscribed",
                description=f"You're already unsubscribed to {ctx.guild}'s announcements and polls.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)
            return

        elif not announcements and not polls:
            await ctx.author.remove_roles(
                discord.Object(announcements_id), reason="Unsubscribed to announcements"
            )
            await ctx.author.remove_roles(
                discord.Object(polls_id), reason="Unsubscribed to polls"
            )
            embed = Embed(
                title=f"{yes_emoji} Unsubscribed",
                description=f"You've unsubscribed to {ctx.guild}'s announcements and polls notifications.",
                color=color,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        elif announcements in ["announcements", "announcement"]:
            if announcements_role not in ctx.author.roles:
                embed = Embed(
                    title=f"{no_emoji} Already unsubscribed",
                    description=f"You're already unsubscribed to {ctx.guild}'s announcements.",
                    color=color,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
            else:
                await ctx.author.remove_roles(
                    discord.Object(announcements_id),
                    reason="Unsubscribed to announcements",
                )
                embed = Embed(
                    title=f"{yes_emoji} Unsubscribed",
                    description=f"You've unsubscribed to {ctx.guild}'s announcements.",
                    color=color,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)

        elif ctx.author.content == "a!polls" or ctx.author.content == "a!poll":
            if polls_role not in ctx.author.roles:
                embed = Embed(
                    title=f"{no_emoji} Already unsubscribed!",
                    description=f"You're already unsubscribed to {ctx.guild}'s polls.",
                    color=color,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
            else:
                await ctx.author.remove_roles(
                    discord.Object(polls_id), reason="Unsubscribed to polls"
                )
                embed = Embed(
                    title=f"{yes_emoji} Unsubscribed",
                    description=f"You've unsubscribed to {ctx.guild}'s polls.",
                    color=color,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)


def setup(bot: Bot) -> None:
    """Load the Subscription cog."""
    bot.add_cog(Subscription(bot))
