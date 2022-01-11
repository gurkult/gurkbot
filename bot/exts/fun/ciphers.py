import hashlib
import logging

from disnake import Embed
from disnake.ext.commands import BadArgument, Cog, Context, group

from bot.bot import Bot
from bot.constants import Colours

logger = logging.getLogger(__name__)


class Ciphers(Cog):
    """Commands for working with ciphers, hashes and encryptions."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group(name="hash", invoke_without_command=True)
    async def hash(
        self,
        ctx: Context,
        algorithm: str,
        *,
        original: str,
    ) -> None:
        """Hashes the passed string and returns the result."""
        if algorithm not in hashlib.algorithms_guaranteed:
            raise BadArgument(
                f"The algorithm `{algorithm}` is not supported. \
                  Run `{ctx.prefix}hash algorithms` for a list of supported algorithms."
            )

        func = getattr(hashlib, algorithm)
        hashed = func(original.encode("utf-8")).hexdigest()

        embed = Embed(
            title=f"Hash ({algorithm})",
            description=hashed,
            colour=Colours.green,
        )
        await ctx.send(embed=embed)

    @hash.command(
        name="algorithms", aliases=("algorithm", "algos", "algo", "list", "l")
    )
    async def algorithms(self, ctx: Context) -> None:
        """Sends a list of all supported hashing algorithms."""
        embed = Embed(
            title="Supported algorithms",
            description="\n".join(
                f"• {algo}" for algo in hashlib.algorithms_guaranteed
            ),  # Shouldn't need pagination
            colour=Colours.green,
        )
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    """Loading the Ciphers cog."""
    bot.add_cog(Ciphers(bot))
