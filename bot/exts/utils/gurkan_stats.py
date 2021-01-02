import re
from typing import Union

from bot.bot import Bot
from discord import Color, Embed, Member
from discord.ext.commands import Cog, Context, command
from fuzzywuzzy import process


RATE_DICT = {
    range(1, 10): "Pathetic",
    range(10, 30): "Not bad",
    range(30, 60): "Good",
    range(60, 80): "Cool!",
    range(80, 95): "So Epic!!",
    range(95, 100): "Just wow, superb!",
}


def gurkan_check(target: Union[list, str]) -> int:
    """Returns the count of gurkans if a list is given or the rate of the gurkan if a string is given."""
    if isinstance(target, list):
        return sum(bool(re.search(r"gurk|urkan", i.lower())) for i in target)
    else:
        return process.extractOne("gurkan", [target])[1]


class GurkanStats(Cog):
    """Commands for showing stats on the Gurkan server."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @command(
        name="gurkancount",
        aliases=(
            "gc",
            "gurkcount",
        ),
        brief="Get the count of people who are valid gurkans",
        help="""gurkancount

            To get the count of people who have gurk/urkan in their names i.e, they are valid gurkans.
            """,
    )
    async def gurkan_count(self, ctx: Context) -> None:
        """
        Goes through a list of all the members and uses regex to check if the member is a gurkan.

        If a member is a gurkan they are added through the generator, and this sum (the count) with a\
        message denoting the quality depending on the rate of total members and total gurkans
        is returned in the end.
        """
        members = [i.display_name for i in ctx.guild.members]

        gurkans = gurkan_check(members)

        rate = round((gurkans / len(members)) * 100)

        if rate == 100:
            await ctx.send(f"Whoa!! Everyone is a gurkan! All {gurkans} members!")
            return
        elif rate == 0:
            await ctx.send("No one is a gurkan?! That's lame.")
            return

        rate_msg = [RATE_DICT[r] for r in RATE_DICT if rate in r][0]

        await ctx.send(
            f"About {rate}% ({gurkans}/ {len(members)}) of members are gurkans, That's {rate_msg}"
        )

    @command(
        name="isgurkan",
        brief="Get an embed on the rate of gurkanity of a user",
        aliases=(
            "gr",
            "gurkanrate",
        ),
        help="""isgurkan [user/text (optional)]

                Get an embed based on the gurkan rate of the person.
            """,
    )
    async def is_gurkan(self, ctx: Context, user: Union[Member, str] = None) -> None:
        """
        Uses fuzzywuzzy module to get a rate on how much the sub string matches the original string,\
        the rate is then sent in a color embed, the color depending on how high the rate is.

        Can be used on other members, or even text.
        """
        if not isinstance(user, str):
            user = ctx.author.display_name if not user else user.display_name

        gurk_rate = gurkan_check(user)
        rate_embed = Embed(description=f"{user}'s gurk rate is {gurk_rate}%")
        color = ""
        title = ""

        if gurk_rate < 40:
            color = Color.red()
            title = ":x: Not gurkan"
        else:
            color = Color.green()
            title = ":cucumber: Gurkan"

        rate_embed.color = color
        rate_embed.title = title

        await ctx.send(embed=rate_embed)


def setup(bot: Bot) -> None:
    """Load the GurkanStats cog."""
    bot.add_cog(GurkanStats(bot))
