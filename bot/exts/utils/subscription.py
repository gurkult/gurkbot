from bot.bot import Bot
from bot.constants import Colors, Emojis, Roles
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog, Context


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
            if role.id == Roles.announcements:
                has_announcements = True
            if role.id == Roles.polls:
                has_polls = True
        if has_announcements and has_polls:
            embed = Embed(
                title=f"{Emojis.warning} Already subscribed",
                description=f"You're already subscribed to {ctx.guild}'s announcements and polls.",
                color=Colors.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)
            return

        elif has_polls:
            await ctx.author.add_roles(
                ctx.guild.get_role(Roles.announcements),
                reason="Subscribed to announcements",
            )
            embed = Embed(
                title=f"{Emojis.confirmation} Subscribed",
                description=f"You've subscribed to {ctx.guild}'s announcements.",
                color=Colors.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        elif has_announcements:
            await ctx.author.add_roles(
                ctx.guild.get_role(Roles.polls),
                reason="Subscribed to polls",
            )
            embed = Embed(
                title=f"{Emojis.confirmation} Subscribed",
                description=f"You've subscribed to {ctx.guild}'s polls.",
                color=Colors.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        else:
            await ctx.author.add_roles(
                ctx.guild.get_role(Roles.announcements),
                reason="Subscribed to announcements",
            )
            await ctx.author.add_roles(
                ctx.guild.get_role(Roles.polls), reason="Subscribed to polls"
            )
            embed = Embed(
                title=f"{Emojis.confirmation} Subscribed",
                description=f"You've subscribed to {ctx.guild}'s announcements and polls.",
                color=Colors.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

    @commands.group(name="unsubscribe", invoke_without_command=True)
    async def unsubscribe_group(self, ctx: Context) -> None:
        """Unsubscribe to announcements and polls notifications by assigning yourself the role."""
        has_announcements = False
        has_polls = False
        for role in ctx.author.roles:
            if role.id == Roles.announcements:
                has_announcements = True
            if role.id == Roles.polls:
                has_polls = True
        if has_announcements and has_polls:
            await ctx.author.remove_roles(
                ctx.guild.get_role(Roles.announcements),
                reason="Unsubscribed to announcements",
            )
            await ctx.author.remove_roles(
                ctx.guild.get_role(Roles.polls), reason="Unsubscribed to polls"
            )
            embed = Embed(
                title=f"{Emojis.confirmation} Unsubscribed",
                description=f"You've unsubscribed to {ctx.guild}'s announcements and polls.",
                color=Colors.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        elif has_polls:
            await ctx.author.remove_roles(
                ctx.guild.get_role(Roles.polls), reason="Unsubscribed to polls"
            )
            embed = Embed(
                title=f"{Emojis.confirmation} Unsubscribed",
                description=f"You've unsubscribed to {ctx.guild}'s polls.",
                color=Colors.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        elif has_announcements:
            await ctx.author.remove_roles(
                ctx.guild.get_role(Roles.announcements),
                reason="Unsubscribed to announcements",
            )
            embed = Embed(
                title=f"{Emojis.confirmation} Unsubscribed",
                description=f"You've unsubscribed to {ctx.guild}'s announcements.",
                color=Colors.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        else:
            embed = Embed(
                title=f"{Emojis.warning} Already unsubscribed",
                description=f"You're already unsubscribed to {ctx.guild}'s announcements and polls.",
                color=Colors.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

    @subscribe_group.command(name="announcements", aliases=("announcement",))
    async def announcements_subscribe(self, ctx: Context) -> None:
        """Subscribe to announcements by assigning yourself the role."""
        for role in ctx.author.roles:
            if role.id == Roles.announcements:
                embed = Embed(
                    title=f"{Emojis.warning} Already subscribed",
                    description=f"You're already subscribed to {ctx.guild}'s announcements.",
                    color=Colors.green,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
                return
        await ctx.author.add_roles(
            ctx.guild.get_role(Roles.announcements),
            reason="Subscribed to announcements",
        )
        embed = Embed(
            title=f"{Emojis.confirmation} Subscribed",
            description=f"You've subscribed to {ctx.guild}'s announcements.",
            color=Colors.green,
        )
        await ctx.send(content=ctx.author.mention, embed=embed)

    @unsubscribe_group.command(name="announcements", aliases=("announcement",))
    async def announcements_unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe to announcements by unassigning yourself the role."""
        has_role = False
        for role in ctx.author.roles:
            if role.id == Roles.announcements:
                has_role = True
                break
        if not has_role:
            embed = Embed(
                title=f"{Emojis.warning} Already unsubscribed",
                description=f"You're already unsubscribed to {ctx.guild}'s announcements.",
                color=Colors.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)
            return
        await ctx.author.remove_roles(
            ctx.guild.get_role(Roles.announcements),
            reason="Unsubscribed to announcements",
        )
        embed = Embed(
            title=f"{Emojis.confirmation} Unsubscribed",
            description=f"You've unsubscribed to {ctx.guild}'s announcements.",
            color=Colors.green,
        )
        await ctx.send(content=ctx.author.mention, embed=embed)

    @subscribe_group.command(name="polls", aliases=("poll",))
    async def polls_subscribe(self, ctx: Context) -> None:
        """Subscribe to polls by assigning yourself the role."""
        for role in ctx.author.roles:
            if role.id == Roles.polls:
                embed = Embed(
                    title=f"{Emojis.warning} Already subscribed",
                    description=f"You're already subscribed to {ctx.guild}'s polls.",
                    color=Colors.green,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
                return
        await ctx.author.add_roles(
            ctx.guild.get_role(Roles.polls), reason="Subscribed to polls"
        )
        embed = Embed(
            title=f"{Emojis.confirmation} Subscribed",
            description=f"You've subscribed to {ctx.guild}'s polls.",
            color=Colors.green,
        )
        await ctx.send(content=ctx.author.mention, embed=embed)

    @unsubscribe_group.command(name="polls", aliases=("poll",))
    async def polls_unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe to polls by unassigning yourself the role."""
        has_role = False
        for role in ctx.author.roles:
            if role.id == Roles.polls:
                has_role = True
                break
        if not has_role:
            embed = Embed(
                title=f"{Emojis.warning} Already unsubscribed",
                description=f"You're already unsubscribed to {ctx.guild}'s polls.",
                color=Colors.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)
            return
        await ctx.author.remove_roles(
            ctx.guild.get_role(Roles.polls), reason="Unsubscribed to polls"
        )
        embed = Embed(
            title=f"{Emojis.confirmation} Unsubscribed",
            description=f"You've unsubscribed to {ctx.guild}'s polls.",
            color=Colors.green,
        )
        await ctx.send(content=ctx.author.mention, embed=embed)


def setup(bot: Bot) -> None:
    """Load the Subscription cog."""
    bot.add_cog(Subscription(bot))
