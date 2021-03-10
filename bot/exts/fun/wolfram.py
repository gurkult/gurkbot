from random import choice
from typing import Union

from aiohttp import ClientSession
from bot.constants import ERROR_REPLIES, Emojis, Tokens
from discord import Embed
from discord.ext import commands
from yarl import URL


class WolframCommands(commands.Cog):
    """
    Wolfram Category cog, containing commands related to the WolframAlpha API.

    Commands
        ├ image         Fetch the response to a query in the form of an image.
        ├ text          Fetch the response to a query in a short phrase.
        └ chat          Fetch the response of the Wolfram AI based on the given question/statement.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.image_url = "http://api.wolframalpha.com/v1/simple"
        self.params = {
            "appid": Tokens.wolfram_id,
            "background": "2F3136",
            "foreground": "white",
            "layout": "labelbar",
            "fontsize": "23",
            "width": "700",
        }

    @staticmethod
    async def web_request(url: str, params: dict) -> Union[URL, str]:
        """Web request handler for wolfram group of commands."""
        async with ClientSession() as session:
            async with session.get(url=url, params=params) as resp:
                if resp.status == 200:
                    return resp.url
                elif resp.status == 501:
                    return "Sorry, the API could not understand your input"
                elif resp.status == 400:
                    return "Sorry, the API did not find any input to interpret"

    @commands.group(name="wolfram", aliases=("wa",), invoke_without_command=True)
    async def wolfram_group(self, ctx: commands.Context) -> None:
        """Commands for wolfram."""
        await ctx.send_help(ctx.command)

    @wolfram_group.command(name="image")
    async def wolfram_image(self, ctx: commands.Context, *, query: str) -> None:
        """Sends wolfram image corresponding to the given query."""
        self.params["i"] = query

        async with ctx.typing():
            response = await WolframCommands.web_request(
                url=self.image_url, params=self.params
            )

            if isinstance(response, str):
                embed = Embed(title=choice(ERROR_REPLIES), description=response)
            else:
                embed = Embed(title=f"{Emojis.wolfram_emoji} Wolfram Alpha").set_image(
                    url=response
                )
                embed.add_field(
                    name="Cannot see image?",
                    value=f"[Click here](https://www.wolframalpha.com/input/?i={query.replace(' ', '+')})",
                )
            await ctx.send(ctx.author.mention, embed=embed)


def setup(bot: commands.Bot) -> None:
    """Load the Wolfram cog."""
    bot.add_cog(WolframCommands(bot))
