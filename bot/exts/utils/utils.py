# Some commands in this file are based on the Python Discord
# "Python" bot, available at https://github.com/python-discord/bot.
# The source code for the bot is available under the MIT-licensed.

import re
import unicodedata
from typing import Tuple

from bot.bot import Bot
from bot.constants import Colours
from bot.utils.pagination import LinePaginator
from discord import Embed, utils
from discord.ext.commands import Cog, Context, command
from discord.ext.commands.errors import BadArgument


class Utils(Cog):
    """A general collection of utilities."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def charinfo(self, ctx: Context, *, characters: str) -> None:
        """Shows you information about up to 50 unicode characters."""
        match = re.match(r"<(a?):(\w+):(\d+)>", characters)
        if match:
            raise BadArgument(
                "Only unicode characters can be processed, but a custom Discord emoji "
                "was found. Please remove it and try again.",
            )
        if len(characters) > 50:
            raise BadArgument(f"Too many characters ({len(characters)}/50)")

        def get_info(char: str) -> Tuple[str, str]:
            digit = f"{ord(char):x}"
            if len(digit) <= 4:
                u_code = f"\\u{digit:>04}"
            else:
                u_code = f"\\U{digit:>08}"
            url = f"https://www.compart.com/en/unicode/U+{digit:>04}"
            name = f"[{unicodedata.name(char, '')}]({url})"
            info = f"`{u_code.ljust(10)}`: {name} - {utils.escape_markdown(char)}"
            return info, u_code

        char_list, raw_list = zip(*(get_info(c) for c in characters))
        embed = Embed(title="Character info", colour=Colours.green)

        if len(characters) > 1:
            # Maximum length possible is 502 out of 1024, so there's no need to truncate.
            embed.add_field(
                name="Full Raw Text", value=f"`{''.join(raw_list)}`", inline=False
            )

        await LinePaginator.paginate(
            char_list, ctx, embed, max_lines=10, max_size=2000, empty=False
        )


def setup(bot: Bot) -> None:
    """Setup Utils cog."""
    bot.add_cog(Utils(bot))
