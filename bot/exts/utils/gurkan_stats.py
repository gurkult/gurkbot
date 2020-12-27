import re

from bot.bot import Bot
from typing import Union
from fuzzywuzzy import process
from discord import Embed, Color, Member
from discord.ext.commands import Cog, command, Context

RATE_DICT = {
    tuple(range(1, 10)): "Pathetic",
    tuple(range(10, 30)): "Not bad",
    tuple(range(30, 60)): "Good",
    tuple(range(60, 80)): "Cool!",
    tuple(range(80, 95)): "So Epic!!",
    tuple(range(95, 100)): "Just wow, superb!"
}


class GurkanStats(Cog):
    """Commands for showing stats on the Gurkan server."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @command(
        brief="Get the count of people who are valid gurkans",
        help="""gurkancount

            To get the count of people who have gurk/urkan in their names i.e,
            they are valid gurkans
            """,
        aliases=("gurkanc", "gcount", "gc", "gurkcount", "gurkc")
    )
    async def gurkancount(self, ctx: Context):
        """Goes through an array of all the members and uses regex to check if the member is a gurkan.
           If the member is not a gurkan, they are not added to the new array and the length of the new array
           with a message denoting the quality depending on the rate of total members and total gurkans
           is returned in the end.
        """

        members = ctx.guild.members

        gurkans = len([1 for i in members if re.search(r"gurk|urkan", i.display_name.lower())])

        rate = round((gurkans / len(members)) * 100)

        if rate == 100:
            await ctx.send(f"Whoa!! Everyone is a gurkan! All {gurkans} members!")
            return
        elif rate == 0:
            await ctx.send("No one is a gurkan?! That's lame.")
            return

        rate_msg = [RATE_DICT[r] for r in RATE_DICT if rate in r][0]

        await ctx.send(f"About {rate}% ({gurkans}/ {len(members)}) of members are gurkans, That's {rate_msg}")

    @command(
        help="""isgurkan [user/text (optional)]

                Get an embed based on the gurkan rate of the person.
            """,
        brief="Get an embed on the rate of gurkanity of a user",
        aliases=("gurkrate", "gr", "isgurk", "gurkanrate", "gurkanr8", "gurkr8")
    )
    async def isgurkan(self, ctx: Context, user: Union[Member, str] = None):
        """
        Uses fuzzywuzzy module to get a rate on how much the sub string matches the original string,
        The rate is then sent in a color embed, the color depending on how high the rate is.
        Can be used on other members, or even text.
        """
        if not isinstance(user, str):
            user = ctx.author.display_name if not user else user.display_name

        gurk_rate = process.extractOne("gurkan", [user])[1]
        rate_embed = Embed(title=f"{user}'s gurk rate is {gurk_rate}%")
        color = ""

        if gurk_rate < 40:
            color = Color.red()
        elif 70 > gurk_rate > 40:
            color = Color.gold()
        elif gurk_rate > 70:
            color = Color.green()

        rate_embed.color = color

        await ctx.send(embed=rate_embed)


def setup(bot: Bot) -> None:
    """Load the GurkanStats cog."""
    bot.add_cog(GurkanStats(bot))
