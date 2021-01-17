import typing

from bot.constants import BOT_REPO_URL
from discord import Embed
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from . import _issues, _profile, _source


class Github(commands.Cog):
    """
    Github Category cog, which contains commands related to github.

    Commands:
        ├ profile       Fetches a user's GitHub information.
        ├ issue         Command to retrieve issue(s) from a GitHub repository.
        └ source        Displays information about the bot's source code.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.group(name="github", aliases=("gh",), invoke_without_command=True)
    async def github_group(self, ctx: commands.Context) -> None:
        """Commands for Github."""
        await ctx.send_help(ctx.command)

    @github_group.command(name="profile")
    @commands.cooldown(1, 10, BucketType.user)
    async def profile(self, ctx: commands.Context, username: str) -> None:
        """
        Fetches a user's GitHub information.

        Username is optional and sends the help command if not specified.
        """
        github_profile = _profile.GithubInfo(self.bot.http_session)
        embed = await github_profile.get_github_info(username)

        await ctx.send(embed=embed)

    @github_group.command(name="issue", aliases=("pr",))
    async def issue(
        self,
        ctx: commands.Context,
        numbers: commands.Greedy[int],
        repository: typing.Optional[str] = None,
    ) -> None:
        """Command to retrieve issue(s) from a GitHub repository."""
        github_issue = _issues.Issues(self.bot.http_session)

        if not numbers:
            raise commands.MissingRequiredArgument(ctx.command.clean_params["numbers"])

        if repository is None:
            user = "gurkult"
        else:
            user, _, repository = repository.rpartition("/")
            if user == "":
                user = "gurkult"

        embed = await github_issue.issue(ctx.message.channel, numbers, repository, user)

        await ctx.send(embed=embed)

    @github_group.command(name="source", aliases=("src", "inspect"))
    async def source_command(
        self, ctx: commands.Context, *, source_item: Optional[str] = None
    ) -> None:
        """Displays information about the bot's source code."""
        if source_item == "":
            embed = Embed(title="Gurkbot's GitHub Repository")
            embed.add_field(name="Repository", value=f"[Go to GitHub]({BOT_REPO_URL})")
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
            return
        elif not ctx.bot.get_command(source_item):
            await ctx.send_help(ctx.command)
            raise commands.BadArgument(
                f"Unable to convert `{source_item}` to valid command or Cog."
            )

        github_source = _source.Source(self.bot.http_session, self.bot.user.avatar_url)
        embed = await github_source.inspect(cmd=ctx.bot.get_command(source_item))

        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Load the Github cog."""
    bot.add_cog(Github(bot))
