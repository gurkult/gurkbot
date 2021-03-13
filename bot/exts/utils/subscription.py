import discord
from bot.bot import Bot
from bot.constants import Colours, Emojis, Roles
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog, Context


class Subscription(Cog):
    """Subscribing and Unsubscrbing to announcements and polls notifications."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def apply_role(self, ctx: Context, role_name: discord.Role) -> bool:
        """Adding Roles and returning True otherwise False."""
        if role_name in ctx.author.roles:
            return False  # user already has the role
        await ctx.author.add_roles(role_name, reason=f"Subscribed to {role_name}")
        return True

    async def de_apply_role(self, ctx: Context, role_name: discord.Role) -> bool:
        """Removing Roles and returning True otherwise False."""
        if role_name in ctx.author.roles:
            await ctx.author.remove_roles(
                role_name, reason=f"Unsubscribed to {role_name}"
            )
            return True
        return False  # user doesn't have the role

    async def subscribe_helper(self, ctx: Context, role_id: int) -> None:
        """Helper function for subscribing to announcements and polls."""
        role_name = ctx.guild.get_role(role_id)
        if await self.apply_role(ctx, role_name):
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} Subscribed",
                description=f"You've subscribed to {ctx.guild}'s {role_name}.",
                color=Colours.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)
        else:
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already subscribed",
                description=f"You're already subscribed to {ctx.guild}'s {role_name}.",
                color=Colours.soft_red,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

    async def unsubscribe_helper(self, ctx: Context, role_id: int) -> None:
        """Helper function for unsubscribing to announcements and polls."""
        role_name = ctx.guild.get_role(role_id)
        if await self.de_apply_role(ctx, role_name):
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} Unsubscribed",
                description=f"You've unsubscribed to {ctx.guild}'s {role_name}.",
                color=Colours.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)
        else:
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already unsubscribed",
                description=f"You're already unsubscribed to {ctx.guild}'s {role_name}.",
                color=Colours.soft_red,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

    async def subscribe_group_helper(self, ctx: Context) -> None:
        """Helper function for subscribe_group."""
        roles = (
            ctx.guild.get_role(Roles.announcements),
            ctx.guild.get_role(Roles.polls),
        )
        role_check = ()

        for i in roles:
            role_check += (await self.apply_role(ctx, i),)

        role_check_dict = {}

        for i in range(len(roles)):
            role_check_dict[roles[i].name] = role_check[i]

        if not any(role_check):
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already subscribed",
                description=f"You're already subscribed to {ctx.guild}'s announcements and polls.",
                color=Colours.soft_red,
            )
        elif all(role_check):
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} Subscribed",
                description=f"You've subscribed to {ctx.guild}'s announcements and polls.",
                color=Colours.green,
            )
        else:
            for i in range(len(roles)):
                if role_check_dict[roles[i].name]:
                    embed = Embed(
                        title=f"{Emojis.confirmation_emoji} Subscribed",
                        description=f"You've subscribed to {ctx.guild}'s announcements.",
                        color=Colours.green,
                    )
                    break
                else:
                    embed = Embed(
                        title=f"{Emojis.confirmation_emoji} Subscribed",
                        description=f"You've subscribed to {ctx.guild}'s polls.",
                        color=Colours.green,
                    )
                    break
        await ctx.send(content=ctx.author.mention, embed=embed)

    async def unsubscribe_group_helper(self, ctx: Context) -> None:
        """Helper function for unsubscribe_group."""
        roles = (
            ctx.guild.get_role(Roles.announcements),
            ctx.guild.get_role(Roles.polls),
        )
        role_check = ()

        for i in roles:
            role_check += (await self.de_apply_role(ctx, i),)

        role_check_dict = {}

        for i in range(len(roles)):
            role_check_dict[roles[i].name] = role_check[i]

        if not any(role_check):
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already unsubscribed",
                description=f"You're already unsubscribed to {ctx.guild}'s announcements and polls.",
                color=Colours.soft_red,
            )
        elif all(role_check):
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} Unsubscribed",
                description=f"You've unsubscribed to {ctx.guild}'s announcements and polls.",
                color=Colours.green,
            )
        else:
            for i in range(len(roles)):
                if role_check_dict[roles[i].name]:
                    embed = Embed(
                        title=f"{Emojis.confirmation_emoji} Unsubscribed",
                        description=f"You've unsubscribed to {ctx.guild}'s announcements.",
                        color=Colours.green,
                    )
                    break
                else:
                    embed = Embed(
                        title=f"{Emojis.confirmation_emoji} Unsubscribed",
                        description=f"You've unsubscribed to {ctx.guild}'s polls.",
                        color=Colours.green,
                    )
                    break
        await ctx.send(content=ctx.author.mention, embed=embed)

    @commands.group(name="subscribe", invoke_without_command=True)
    async def subscribe_group(self, ctx: Context) -> None:
        """Subscribe to announcements and polls notifications by assigning yourself the role."""
        await self.subscribe_group_helper(ctx)

    @commands.group(name="unsubscribe", invoke_without_command=True)
    async def unsubscribe_group(self, ctx: Context) -> None:
        """Unsubscribe to announcements and polls notifications by assigning yourself the role."""
        await self.unsubscribe_group_helper(ctx)

    @subscribe_group.command(name="announcements", aliases=("announcement",))
    async def announcements_subscribe(self, ctx: Context) -> None:
        """Subscribe to announcements by assigning yourself the role."""
        await self.subscribe_helper(ctx, Roles.announcements)

    @unsubscribe_group.command(name="announcements", aliases=("announcement",))
    async def announcements_unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe to announcements by assigning yourself the role."""
        await self.unsubscribe_helper(ctx, Roles.announcements)

    @subscribe_group.command(name="polls", aliases=("poll",))
    async def polls_subscribe(self, ctx: Context) -> None:
        """Subscribe to polls by assigning yourself the role."""
        await self.subscribe_helper(ctx, Roles.polls)

    @unsubscribe_group.command(name="polls", aliases=("poll",))
    async def polls_unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe to polls by assigning yourself the role."""
        await self.unsubscribe_helper(ctx, Roles.polls)


def setup(bot: Bot) -> None:
    """Load the Subscription cog."""
    bot.add_cog(Subscription(bot))
