import typing

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from . import _issues, _profile, _source


class Github(commands.Cog):
    """Github."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.group(name="github", aliases=("gh",), invoke_without_command=True)
    async def github_group(self, ctx: commands.Context) -> None:
        """Commands for Github."""
        await ctx.send_help(ctx.command)

    @github_group.command(name="profile")
    @commands.cooldown(1, 10, BucketType.user)
    async def profile(
        self, ctx: commands.Context, username: typing.Optional[str]
    ) -> None:
        """
        Fetches a user's GitHub information.

        Username is optional and sends the help command if not specified.
        """
        github_profile = _profile.GithubInfo(self.bot.http_session)
        embed = await github_profile.get_github_info(username)

        if embed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)
            return

        await ctx.send(embed=embed)

    @github_group.command(name="issue", aliases=("pr",))
    async def issue(
        self,
        ctx: commands.Context,
        numbers: commands.Greedy[int],
        repository: str = "",
        user: str = "gurkult",
    ) -> None:
        """Command to retrieve issue(s) from a GitHub repository."""
        github_issue = _issues.Issues(self.bot.http_session)

        if not numbers:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)
            return

        embed = await github_issue.issue(
            ctx.message.channel.id, numbers, repository, user
        )

        if embed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)
            return

        await ctx.send(embed=embed)

    @github_group.command(name="source", aliases=("src", "inspect"))
    async def source_command(self, ctx: commands.Context, *, source_item: str) -> None:
        """Displays information about the bot's source code."""
        github_source = _source.Source(self.bot.http_session, self.bot.user.avatar_url)
        embed = await github_source.inspect(cmd=ctx.bot.get_command(source_item))

        if embed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)
            return

        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Load the Github cog."""
    bot.add_cog(Github(bot))
