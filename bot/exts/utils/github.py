from discord.ext import commands
from discord.ext.commands import Cog
from discord import Embed
import aiohttp
import random

from bot.bot import Bot
from bot.constants import PREFIX

GREEN = 0x1F8B4C
GITHUB_LOGO_URL = (
    "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
)


class GitHub(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command(help="Get the top 5 contributors of the bot.")
    async def contributors(self, ctx):
        """Command for getting the contributors of the bot."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                "https://api.github.com/repos/gurkult/gurkbot/contributors"
            ) as resp:
                response = await resp.json()
                response = random.sample(response, 5)
        em = Embed(
            title="Awesome People Who have contributed to this Bot!", color=GREEN
        )
        em.set_thumbnail(
            url="https://avatars3.githubusercontent.com/u/72938830?s=200&v=4"
        )
        for contributor in response:
            em.add_field(
                name=contributor["login"],
                value="{} commits\n[Profile](https://github.com/{})".format(
                    contributor["contributions"], contributor["login"]
                ),
            )
        em.add_field(
            name="You Can Contribute Too!",
            value="Here's our [GitHub Repo](https://github.com/gurkult/gurkbot)",
        )
        await ctx.send(embed=em)

    @commands.group()
    async def gitsearch(self, ctx: commands.Context):
        """Group of the commands for searching GitHub"""
        help_msg = f"Use `{PREFIX}gitsearch users username` to search for users\
         and `{PREFIX}gitsearch repos reponame` to search for repositories."
        if ctx.invoked_subcommand is None:
            await ctx.send(help_msg)

    @gitsearch.command()
    async def users(self, ctx: commands.Context, *, term):
        """Command for searching users on GitHub. A sub command on the gitsearch group."""
        async with aiohttp.ClientSession() as client:
            async with client.get(
                "https://api.github.com/search/users?q=" + str(term.replace(" ", "+"))
            ) as resp:
                assert resp.status == 200
                response = await resp.json()
        results_count = response["total_count"]
        if results_count == 0:
            await ctx.send("No Results Found.")
        else:
            results_embed = Embed(
                title=f"{results_count} results for {term}", color=GREEN
            )
            results_embed.set_thumbnail(url=GITHUB_LOGO_URL)
            if len(response["items"]) > 3:
                for user in response["items"][-10:]:
                    profile_link = user["html_url"]
                    results_embed.add_field(
                        name=user["login"], value=profile_link, inline=False
                    )

                await ctx.send(embed=results_embed)
            elif len(response["items"]) <= 3:
                absolute_result = response["items"][0]
                absolute_result_embed = Embed(
                    title=absolute_result["login"], color=GREEN
                )
                absolute_result_embed.set_thumbnail(url=absolute_result["avatar_url"])
                absolute_result_embed.add_field(
                    name="Profile", value=absolute_result["html_url"]
                )
                await ctx.send(embed=absolute_result_embed)

    @gitsearch.command()
    async def repos(self, ctx: commands.Context, *, term):
        """Command for searching repositories on GitHub. A sub command on the gitsearch group."""
        async with aiohttp.ClientSession() as client:
            async with client.get(
                "https://api.github.com/search/repositories?q="
                + str(term.replace(" ", "+"))
            ) as resp:
                assert resp.status == 200
                response = await resp.json()
        results_count = response["total_count"]
        if results_count == 0:
            await ctx.send("No results found.")
        else:
            results_embed = Embed(
                title=f"{results_count} Results for {term}", color=GREEN
            )
            results_embed.set_thumbnail(url=GITHUB_LOGO_URL)

            if len(response["items"]) > 3:
                for result in response["items"][-10:]:
                    repo_link = result["html_url"]
                    results_embed.add_field(
                        name=result["full_name"], value=f"{repo_link}", inline=False
                    )
                await ctx.send(embed=results_embed)
            elif len(response["items"]) <= 3:
                absolute_result = response["items"][0]
                absolute_result_link = absolute_result["html_url"]
                absolute_result_embed = Embed(
                    title=absolute_result["full_name"], color=GREEN
                )
                absolute_result_embed.set_thumbnail(
                    url=absolute_result["owner"]["avatar_url"]
                )
                absolute_result_embed.add_field(
                    name="Description",
                    value=absolute_result["description"],
                    inline=False,
                )
                absolute_result_embed.add_field(
                    name="Most Used Language",
                    value=absolute_result["language"],
                    inline=False,
                )
                absolute_result_embed.add_field(
                    name="Forks", value=absolute_result["forks_count"], inline=False
                )
                absolute_result_embed.add_field(
                    name="Repository", value=absolute_result_link, inline=True
                )
                await ctx.send(embed=absolute_result_embed)


def setup(bot) -> None:
    bot.add_cog(GitHub(bot))
