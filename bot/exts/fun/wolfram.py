import random
from typing import Union
from urllib import parse

import disnake
from bot.constants import ERROR_REPLIES, Emojis, Tokens
from disnake import Embed
from disnake.ext import commands
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
        self.image_url = "https://api.wolframalpha.com/v1/simple"
        self.params = {
            "appid": Tokens.wolfram_token,
            "background": "2F3136",
            "foreground": "white",
            "layout": "labelbar",
            "fontsize": "23",
            "width": "700",
        }

    async def web_request(self, url: str, params: dict) -> Union[URL, str]:
        """Web request handler for wolfram group of commands."""
        async with self.bot.http_session as session:
            async with session.get(url=url, params=params) as resp:
                if resp.status == 200:
                    return resp.url
                elif resp.status == 501:
                    return "Sorry, the API could not understand your input"
                elif resp.status == 400:
                    return "Sorry, the API did not find any input to interpret"

    @commands.slash_command(guild_ids=[793864455527202847])
    async def wolfram(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Commands for wolfram."""

    @wolfram.sub_command()
    async def image(
        self, inter: disnake.ApplicationCommandInteraction, query: str
    ) -> None:
        """
        Send wolfram image corresponding to the given query.

        Parameters
        ----------
        query: The user query.
        """
        await inter.response.defer()

        self.params["i"] = query

        response = await self.web_request(url=self.image_url, params=self.params)

        if isinstance(response, str):
            embed = Embed(title=random.choice(ERROR_REPLIES), description=response)
        else:
            original_url = parse.quote_plus(query)
            embed = Embed(title=f"{Emojis.wolfram_emoji} Wolfram Alpha")
            embed.set_image(url=str(response))
            embed.add_field(
                name="Cannot see image?",
                value=f"[Click here](https://www.wolframalpha.com/input/?i={original_url})",
            )

        await inter.edit_original_message(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Load the Wolfram cog."""
    bot.add_cog(WolframCommands(bot))
