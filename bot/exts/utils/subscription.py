from typing import Callable

from disnake import Embed, Role
from disnake.ext.commands import Cog, Context, group

from bot.bot import Bot
from bot.constants import Colours, Emojis, Roles


class Subscription(Cog):
    """Subscribe and Unsubscribe to announcements and polls notifications."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    async def get_roles(ctx: Context) -> tuple:
        """Gets announcements and polls role from the guild of the context."""
        return (
            ctx.guild.get_role(Roles.announcements),
            ctx.guild.get_role(Roles.polls),
            ctx.guild.get_role(Roles.events),
        )

    @staticmethod
    async def apply_role(ctx: Context, role_name: Role) -> bool:
        """
        Applies the provided role to the user.

        Returns `True` if role was successfully added otherwise it returns `False`.
        """
        if role_name in ctx.author.roles:
            return False  # User already has the role
        await ctx.author.add_roles(role_name, reason=f"Subscribed to {role_name}")
        return True

    @staticmethod
    async def remove_role(ctx: Context, role_name: Role) -> bool:
        """
        Removes the provided role from the user.

        Returns `True` if role was successfully removed otherwise it returns `False`.
        """
        if role_name in ctx.author.roles:
            await ctx.author.remove_roles(
                role_name, reason=f"Unsubscribed to {role_name}"
            )
            return True
        return False  # User doesn't have the role

    async def sub_unsub_helper(
        self, ctx: Context, role_id: int, func: Callable, action: str
    ) -> None:
        """
        Helper function for sending embeds for subscribe and unsubscribe to announcements or polls.

        If `func` is `apply_role`, it checks if user have the role (returns `False`) or not (returns `True`)
        If `func` is `remove_role`, it checks if user have the role (returns `True`) or not (returns `False`)
        """
        role_name = ctx.guild.get_role(role_id)
        if await func(ctx, role_name):
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} {action}",
                description=f"You've {action.lower()} to {ctx.guild}'s {role_name}.",
                color=Colours.green,
            )
        else:
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already {action.lower()}",
                description=f"You're already {action.lower()} to {ctx.guild}'s {role_name}.",
                color=Colours.soft_red,
            )
        await ctx.send(content=ctx.author.mention, embed=embed)

    async def sub_unsub_group_helper(
        self, ctx: Context, func: Callable, action: str
    ) -> None:
        """
        Helper function for subscribe_group and unsubscribe_group.

        If `func` is `apply_role`, `role_lst` stores the role(s) which are added to the user
        If `func` is `remove_role`, `role_lst` stores the role(s) which are removed from the user
        """
        roles = await self.get_roles(ctx)
        role_lst = [
            role.name for role in roles if await func(ctx, role)
        ]  # Applies/Removes the role(s) and stores a list of applied/removed role(s)
        if role_lst:
            msg = (
                f"{', '.join(role_lst[:-1])} and {role_lst[-1]}"
                if len(role_lst) > 1
                else role_lst[0]
            )  # Stores a string which tells what role(s) is/are added to or removed from the user
            embed = Embed(
                title=f"{Emojis.confirmation_emoji} {action}",
                description=f"You've {action.lower()} to {ctx.guild}'s {msg}.",
                color=Colours.green,
            )
        else:
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already {action.lower()}",
                description=f"You're already {action.lower()} to {ctx.guild}'s announcements and polls.",
                color=Colours.soft_red,
            )
        await ctx.send(content=ctx.author.mention, embed=embed)

    async def subscribe_list(self, ctx: Context) -> None:
        """Sends an embed for list of Roles that you can subscribe to."""
        roles = await self.get_roles(ctx)
        escape = "\n- "
        embed = Embed(
            title=f"{Emojis.confirmation_emoji} Subscribe List",
            description=f"- {escape.join(role.name for role in roles)}",  # Creates a bullet list
            color=Colours.green,
        )
        await ctx.send(content=ctx.author.mention, embed=embed)

    @group(name="subscribe", aliases=("sub",), invoke_without_command=True)
    async def subscribe_group(self, ctx: Context) -> None:
        """Subscribe to announcements and polls notifications, by assigning yourself the roles."""
        await self.sub_unsub_group_helper(ctx, self.apply_role, "Subscribed")

    @subscribe_group.command(name="announcements", aliases=("announcement",))
    async def announcements_subscribe(self, ctx: Context) -> None:
        """Subscribe to announcements notifications, by assigning yourself the role."""
        await self.sub_unsub_helper(
            ctx, Roles.announcements, self.apply_role, "Subscribed"
        )

    @subscribe_group.command(name="polls", aliases=("poll",))
    async def polls_subscribe(self, ctx: Context) -> None:
        """Subscribe to polls notification, by assigning yourself the role."""
        await self.sub_unsub_helper(ctx, Roles.polls, self.apply_role, "Subscribed")

    @subscribe_group.command(name="events", aliases=("event",))
    async def events_subscribe(self, ctx: Context) -> None:
        """Subscribe to events notification, by assigning yourself the role."""
        await self.sub_unsub_helper(ctx, Roles.events, self.apply_role, "Subscribed")

    @group(name="unsubscribe", aliases=("unsub",), invoke_without_command=True)
    async def unsubscribe_group(self, ctx: Context) -> None:
        """Unsubscribe to announcements and polls notifications, by removing your roles."""
        await self.sub_unsub_group_helper(ctx, self.remove_role, "Unsubscribed")

    @unsubscribe_group.command(name="announcements", aliases=("announcement",))
    async def announcements_unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe to announcements notification, by removing your role."""
        await self.sub_unsub_helper(
            ctx, Roles.announcements, self.remove_role, "Unsubscribed"
        )

    @unsubscribe_group.command(name="polls", aliases=("poll",))
    async def polls_unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe to polls notification, by removing your role."""
        await self.sub_unsub_helper(ctx, Roles.polls, self.remove_role, "Unsubscribed")

    @unsubscribe_group.command(name="events", aliases=("event",))
    async def events_unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe to events notification, by removing your role."""
        await self.sub_unsub_helper(ctx, Roles.events, self.remove_role, "Unsubscribed")

    @group(name="subscribelist", aliases=("sublist",), invoke_without_command=True)
    async def subscribelist(self, ctx: Context) -> None:
        """Gives a list of roles that you can subscribe to."""
        await self.subscribe_list(ctx)


def setup(bot: Bot) -> None:
    """Load the Subscription cog."""
    bot.add_cog(Subscription(bot))
