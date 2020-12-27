import re

from bot.bot import Bot
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


def setup(bot: Bot) -> None:
    """Load the GurkanStats cog."""
    bot.add_cog(GurkanStats(bot))
