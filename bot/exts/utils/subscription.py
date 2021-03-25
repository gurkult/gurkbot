from bot.bot import Bot
from bot.constants import Colours, Emojis, Roles
from discord import Embed, Role
from discord.ext.commands import Cog, Context, group


class Subscription(Cog):
    """Subscribing and Unsubscrbing to announcements and polls notifications."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def get_roles(self, ctx: Context) -> tuple:
        """Returns a `tuple` with all the roles that you can subscribe/unsubscribe to."""
        roles = (
            ctx.guild.get_role(Roles.announcements),
            ctx.guild.get_role(Roles.polls),
        )
        return roles

    async def apply_role(self, ctx: Context, role_name: Role) -> bool:
        """Returns `True` if role is successfully added otherwise it returns `False`."""
        if role_name in ctx.author.roles:
            return False  # user already has the role
        await ctx.author.add_roles(role_name, reason=f"Subscribed to {role_name}")
        return True

    async def de_apply_role(self, ctx: Context, role_name: Role) -> bool:
        """Returns `True` if role is successfully removed otherwise it returns `False`."""
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
        """Helper function for subscribe_group. Sends embed for role subscription."""
        roles = await self.get_roles(ctx)
        role_lst = [role.name for role in roles if await self.apply_role(ctx, role)]
        if len(role_lst) != 0:
            msg = (
                f"{', '.join(role_lst[:-1])} and {role_lst[-1]}"
                if len(role_lst) > 1
                else role_lst[0]
            )  # stores a string which tells what roles are added to the user
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} Subscribed",
                description=f"You've subscribed to {ctx.guild}'s {msg}.",
                color=Colours.green,
            )
        else:
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already subscribed",
                description=f"You're already subscribed to {ctx.guild}'s announcements and polls.",
                color=Colours.soft_red,
            )
        await ctx.send(content=ctx.author.mention, embed=embed)

    async def unsubscribe_group_helper(self, ctx: Context) -> None:
        """Helper function for unsubscribe_group. Sends embed for role unsubscription."""
        roles = await self.get_roles(ctx)
        role_lst = [role.name for role in roles if await self.de_apply_role(ctx, role)]
        if len(role_lst) != 0:
            msg = (
                f"{', '.join(role_lst[:-1])} and {role_lst[-1]}"
                if len(role_lst) > 1
                else role_lst[0]
            )  # stores a string which tells what roles are removed from the user
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} Unsubscribed",
                description=f"You've unsubscribed to {ctx.guild}'s {msg}.",
                color=Colours.green,
            )
        else:
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already unsubscribed",
                description=f"You're already unsubscribed to {ctx.guild}'s announcements and polls.",
                color=Colours.soft_red,
            )
        await ctx.send(content=ctx.author.mention, embed=embed)

    @group(name="subscribe", invoke_without_command=True)
    async def subscribe_group(self, ctx: Context) -> None:
        """Subscribe to announcements and polls notifications, by assigning yourself the roles."""
        await self.subscribe_group_helper(ctx)

    @group(name="unsubscribe", invoke_without_command=True)
    async def unsubscribe_group(self, ctx: Context) -> None:
        """Unsubscribe to announcements and polls notifications, by removing your roles."""
        await self.unsubscribe_group_helper(ctx)

    @subscribe_group.command(name="announcements", aliases=("announcement",))
    async def announcements_subscribe(self, ctx: Context) -> None:
        """Subscribe to announcements by assigning yourself the role."""
        await self.subscribe_helper(ctx, Roles.announcements)

    @unsubscribe_group.command(name="announcements", aliases=("announcement",))
    async def announcements_unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe to announcements by removing your role."""
        await self.unsubscribe_helper(ctx, Roles.announcements)

    @subscribe_group.command(name="polls", aliases=("poll",))
    async def polls_subscribe(self, ctx: Context) -> None:
        """Subscribe to polls by assigning yourself the role."""
        await self.subscribe_helper(ctx, Roles.polls)

    @unsubscribe_group.command(name="polls", aliases=("poll",))
    async def polls_unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe to polls by removing your role."""
        await self.unsubscribe_helper(ctx, Roles.polls)


def setup(bot: Bot) -> None:
    """Load the Subscription cog."""
    bot.add_cog(Subscription(bot))
