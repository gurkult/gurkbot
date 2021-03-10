import asyncio
import functools
from concurrent import futures
from io import BytesIO

import discord
from PIL import Image, ImageDraw, ImageFile, ImageSequence
from discord.ext import commands

ImageFile.LOAD_TRUNCATED_IMAGES = True

LARGE_DIAMETER = 110
SMALL_DIAMETER = 80

# Two masks, one for the normal size, and a smaller one for the final stage of the bonk
LARGE_MASK = Image.new("L", (LARGE_DIAMETER,) * 2)
draw = ImageDraw.Draw(LARGE_MASK)
draw.ellipse((0, 0, LARGE_DIAMETER, LARGE_DIAMETER), fill=255)

SMALL_MASK = Image.new("L", (SMALL_DIAMETER,) * 2)
draw = ImageDraw.Draw(SMALL_MASK)
draw.ellipse((0, 0, SMALL_DIAMETER, SMALL_DIAMETER), fill=255)

BONK_GIF = Image.open("bot/resources/images/yodabonk.gif")

PFP_ENTRY_FRAME = 31
BONK_FRAME = 43
PFP_EXIT_FRAME = 56
PFP_CENTRE = (355, 73)


class Bonk(commands.Cog):
    """Cog for sending bonking gifs."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def _generate_gif(pfp: bytes) -> BytesIO:
        pfp = Image.open(BytesIO(pfp))
        pfps = [pfp.resize((LARGE_DIAMETER,) * 2), pfp.resize((SMALL_DIAMETER,) * 2)]

        out_images = []

        for i, frame in enumerate(ImageSequence.Iterator(BONK_GIF)):
            canvas = Image.new("RGBA", BONK_GIF.size)
            canvas.paste(frame.convert("RGBA"), (0, 0))

            if PFP_ENTRY_FRAME <= i <= PFP_EXIT_FRAME:
                if i == BONK_FRAME:
                    canvas.paste(
                        pfps[1],
                        (
                            PFP_CENTRE[0] - SMALL_DIAMETER // 2,
                            PFP_CENTRE[1]
                            - SMALL_DIAMETER // 2
                            + 10,  # Shift avatar down by 10 px in the bonk frame
                        ),
                        SMALL_MASK,
                    )
                else:
                    canvas.paste(
                        pfps[0],
                        (
                            PFP_CENTRE[0] - LARGE_DIAMETER // 2,
                            PFP_CENTRE[1] - LARGE_DIAMETER // 2,
                        ),
                        LARGE_MASK,
                    )

            out_images.append(canvas)

        out_gif = BytesIO()
        out_images[0].save(
            out_gif,
            "GIF",
            save_all=True,
            append_images=out_images[1:],
            loop=0,
            duration=50,
        )
        return out_gif

    @commands.command()
    @commands.max_concurrency(3)
    async def bonk(self, ctx: commands.Context, member: discord.Member) -> None:
        """Sends gif of mentioned member being bonked [whacked by Yoda]."""
        pfp = await member.avatar_url.read()
        created_at = ctx.message.created_at.strftime("%Y-%m-%d_%H-%M-%S-%f")
        out_filename = f"bonk_{member.display_name}_{created_at}.gif"
        func = functools.partial(self._generate_gif, pfp)

        async with ctx.typing():
            with futures.ProcessPoolExecutor() as pool:
                out_gif = await asyncio.get_running_loop().run_in_executor(pool, func)

        embed = discord.Embed(title=f"Get bonkt {member.display_name}!")
        embed.set_image(url=f"attachment://{out_filename}")

        out_gif.seek(0)
        await ctx.send(file=discord.File(out_gif, out_filename), embed=embed)


def setup(bot: commands.Bot) -> None:
    """Load the Bonk cog."""
    bot.add_cog(Bonk(bot))
