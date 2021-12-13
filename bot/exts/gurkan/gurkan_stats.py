from typing import Optional, Union

from bot.bot import Bot
from bot.constants import Emojis
from bot.utils.is_gurkan import gurkan_check, gurkan_rate
from disnake import Color, Embed, Member
from disnake.ext.commands import Cog, Context, command


RATE_DICT = {
    range(1, 10): "pathetic",
    range(10, 30): "not bad",
    range(30, 60): "good",
    range(60, 80): "cool!",
    range(80, 95): "so Epic!!",
    range(95, 100): "just wow, superb!",
}


class GurkanStats(Cog):
    """Commands for showing stats on the Gurkan server."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(
        name="gurkancount",
        aliases=(
            "gc",
            "gurkcount",
        ),
        brief="Get the count of people who are valid gurkans",
        help="""gurkancount

            Get the count of people who are valid gurkans.
            """,
    )
    async def gurkan_count(self, ctx: Context) -> None:
        """
        Goes through a list of all the members and uses regex to check if the member is a gurkan.

        Sends the count of total Gurkans in the server,\
        and the percentage of the gurkans to the server members.
        """
        members = ctx.guild.members
        gurkans = sum(gurkan_check(member.display_name) for member in members)
        rate = round((gurkans / len(members)) * 100)

        count_emb = Embed()

        if rate == 100:
            title = f"Whoa!! All {gurkans} members are gurkans!"
            color = Color.green()

        elif rate == 0:
            title = "No one is a gurkan?! That's lame."
            color = Color.red()

        else:
            rate_m = [RATE_DICT[r] for r in RATE_DICT if rate in r][0]

            title = f"{Emojis.cucumber_emoji} {gurkans} members"
            color = Color.green()
            description = f"About {rate}% ({gurkans}/ {len(members)}) of members are gurkans, that's {rate_m}"

        count_emb.title = title
        count_emb.color = color
        count_emb.description = description

        await ctx.send(embed=count_emb)

    @command(
        name="isgurkan",
        brief="Get an embed of how gurkan a user is",
        aliases=("gr", "gurkanrate", "gurkrate", "isgurk"),
        help="""isgurkan [user/text (optional)]

                Check if someone is gurkan and get their gurkanrate.
            """,
    )
    async def is_gurkan(
        self, ctx: Context, *, user: Optional[Union[Member, str]]
    ) -> None:
        """
        The gurkanrate of the user and whether the user is a gurkan is sent in an embed,\
        the color depending on how high the rate is.

        Can be used on other members, or even text.
        """
        if not isinstance(user, str):
            user = user.display_name if user else ctx.author.display_name

        gurk_state = gurkan_check(user)
        gurk_rate = gurkan_rate(user)
        rate_embed = Embed(description=f"{user}'s gurk rate is {gurk_rate}%")

        if not gurk_state:
            color = Color.red()
            title = f"{Emojis.invalid_emoji} Not gurkan"
        else:
            color = Color.green()
            title = f"{Emojis.cucumber_emoji} Gurkan"

        rate_embed.color = color
        rate_embed.title = title

        await ctx.send(embed=rate_embed)


def setup(bot: Bot) -> None:
    """Load the GurkanStats cog."""
    bot.add_cog(GurkanStats(bot))
