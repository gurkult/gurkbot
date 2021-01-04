from bot.bot import Bot
from bot.constants import Colors, Emojis, Roles
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog, Context


class Subscription(Cog):
    """Subscribing and Unsubscrbing to announcements and polls notifications."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def sub_unsub_helper(
        self,
        ctx: Context,
        sub_unsub: str,
        role_id1: int = Roles.announcements,
        role_id2: int = Roles.polls,
        role_name1: str = "announcements",
        role_name2: str = "polls",
    ) -> None:
        """Subscribe group and Unsubscribe group helper."""
        has_announcements = False
        has_polls = False
        for role in ctx.author.roles:
            if role.id == role_id1:
                has_announcements = True
            if role.id == role_id2:
                has_polls = True
        if has_announcements and has_polls:
            if sub_unsub == "Subscribed":
                embed = Embed(
                    title=f"{Emojis.warning_emoji} Already {sub_unsub.lower()}",
                    description=f"""You're already {sub_unsub.lower()} to {ctx.guild}'s \
                    {role_name1} and {role_name2}.""",
                    color=Colors.green,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
                return
            else:
                await ctx.author.remove_roles(
                    ctx.guild.get_role(role_id1),
                    reason=f"{sub_unsub} to {role_name1}",
                )
                await ctx.author.remove_roles(
                    ctx.guild.get_role(role_id2), reason=f"{sub_unsub} to {role_name2}"
                )
                embed = Embed(
                    title=f"{Emojis.confirmation_emoji} {sub_unsub}",
                    description=f"""You've {sub_unsub.lower()} to {ctx.guild}'s \
                    {role_name1} and {role_name2}.""",
                    color=Colors.green,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)

        elif has_polls:
            if sub_unsub == "Subscribed":
                await ctx.author.add_roles(
                    ctx.guild.get_role(role_id1),
                    reason=f"{sub_unsub} to {role_name1}",
                )
                embed = Embed(
                    title=f"{Emojis.confirmation_emoji} {sub_unsub}",
                    description=f"You've {sub_unsub.lower()} to {ctx.guild}'s {role_name1}.",
                    color=Colors.green,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
            else:
                await ctx.author.remove_roles(
                    ctx.guild.get_role(role_id2),
                    reason=f"{sub_unsub} to {role_name2}",
                )
                embed = Embed(
                    title=f"{Emojis.confirmation_emoji} {sub_unsub}",
                    description=f"You've {sub_unsub.lower()} to {ctx.guild}'s {role_name2}.",
                    color=Colors.green,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
        elif has_announcements:
            if sub_unsub == "Subscribed":
                await ctx.author.add_roles(
                    ctx.guild.get_role(role_id2),
                    reason=f"{sub_unsub} to {role_name2}",
                )
                embed = Embed(
                    title=f"{Emojis.confirmation_emoji} {sub_unsub}",
                    description=f"You've {sub_unsub.lower()} to {ctx.guild}'s {role_name2}.",
                    color=Colors.green,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
            else:
                await ctx.author.remove_roles(
                    ctx.guild.get_role(role_id1),
                    reason=f"{sub_unsub} to {role_name1}",
                )
                embed = Embed(
                    title=f"{Emojis.confirmation_emoji} {sub_unsub}",
                    description=f"You've {sub_unsub.lower()} to {ctx.guild}'s {role_name1}.",
                    color=Colors.green,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
        else:
            if sub_unsub == "Subscribed":
                await ctx.author.add_roles(
                    ctx.guild.get_role(role_id1),
                    reason=f"{sub_unsub} to {role_name1}",
                )
                await ctx.author.add_roles(
                    ctx.guild.get_role(role_id2), reason=f"{sub_unsub} to {role_name2}"
                )
                embed = Embed(
                    title=f"{Emojis.confirmation_emoji} {sub_unsub}",
                    description=f"""You've {sub_unsub.lower()} to {ctx.guild}'s \
                    {role_name1} and {role_name2}.""",
                    color=Colors.green,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
            else:
                embed = Embed(
                    title=f"{Emojis.warning_emoji} Already {sub_unsub.lower()}",
                    description=f"""You're already {sub_unsub.lower()} to {ctx.guild}'s \
                    {role_name1} and {role_name2}.""",
                    color=Colors.green,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)

    async def subscribe_helper(
        self, ctx: Context, role_id: int, role_name: str
    ) -> None:
        """Subscribe helper function."""
        for role in ctx.author.roles:
            if role.id == role_id:
                embed = Embed(
                    title=f"{Emojis.warning_emoji} Already subscribed",
                    description=f"You're already subscribed to {ctx.guild}'s {role_name}.",
                    color=Colors.green,
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
                return
        await ctx.author.add_roles(
            ctx.guild.get_role(role_id),
            reason=f"Subscribed to {role_name}",
        )
        embed = Embed(
            title=f"{Emojis.confirmation_emoji} Subscribed",
            description=f"You've subscribed to {ctx.guild}'s {role_name}.",
            color=Colors.green,
        )
        await ctx.send(content=ctx.author.mention, embed=embed)

    async def unsubscribe_helper(
        self, ctx: Context, role_id: int, role_name: str
    ) -> None:
        """Unsubscribe helper function."""
        has_role = False
        for role in ctx.author.roles:
            if role.id == role_id:
                has_role = True
                break
        if not has_role:
            embed = Embed(
                title=f"{Emojis.warning_emoji} Already unsubscribed",
                description=f"You're already unsubscribed to {ctx.guild}'s {role_name}.",
                color=Colors.green,
            )
            await ctx.send(content=ctx.author.mention, embed=embed)
            return
        await ctx.author.remove_roles(
            ctx.guild.get_role(role_id),
            reason=f"Unsubscribed to {role_name}",
        )
        embed = Embed(
            title=f"{Emojis.confirmation_emoji} Unsubscribed",
            description=f"You've unsubscribed to {ctx.guild}'s {role_name}.",
            color=Colors.green,
        )
        await ctx.send(content=ctx.author.mention, embed=embed)

    @commands.group(name="subscribe", invoke_without_command=True)
    async def subscribe_group(self, ctx: Context) -> None:
        """Subscribe to announcements and polls notifications by assigning yourself the role."""
        await self.sub_unsub_helper(ctx, "Subscribed")

    @commands.group(name="unsubscribe", invoke_without_command=True)
    async def unsubscribe_group(self, ctx: Context) -> None:
        """Unsubscribe to announcements and polls notifications by assigning yourself the role."""
        await self.sub_unsub_helper(ctx, "Unsubscribed")

    @subscribe_group.command(name="announcements", aliases=("announcement",))
    async def announcements_subscribe(self, ctx: Context) -> None:
        """Subscribe to announcements by assigning yourself the role."""
        await self.subscribe_helper(ctx, Roles.announcements, "announcements")

    @unsubscribe_group.command(name="announcements", aliases=("announcement",))
    async def announcements_unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe to announcements by unassigning yourself the role."""
        await self.unsubscribe_helper(ctx, Roles.announcements, "announcements")

    @subscribe_group.command(name="polls", aliases=("poll",))
    async def polls_subscribe(self, ctx: Context) -> None:
        """Subscribe to polls by assigning yourself the role."""
        await self.subscribe_helper(ctx, Roles.polls, "polls")

    @unsubscribe_group.command(name="polls", aliases=("poll",))
    async def polls_unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe to polls by unassigning yourself the role."""
        await self.unsubscribe_helper(ctx, Roles.polls, "polls")


def setup(bot: Bot) -> None:
    """Load the Subscription cog."""
    bot.add_cog(Subscription(bot))
