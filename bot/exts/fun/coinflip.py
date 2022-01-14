
import disnake
from bot.bot import Bot
import random

from disnake.ext import commands
from disnake.ext.commands import Context


class Choice(disnake.ui.View):
    """Choosing heads or tails."""

    def __init__(self):
        super().__init__()
        self.choice = None

    @disnake.ui.button(label="Heads", style=disnake.ButtonStyle.blurple)
    async def confirm(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        """Heads button."""
        self.choice = button.label.lower()
        self.stop()

    @disnake.ui.button(label="Tails", style=disnake.ButtonStyle.blurple)
    async def cancel(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        """Tails button."""
        self.choice = button.label.lower()
        self.stop()


@commands.command(
    name="coinflip",
    description="The bot tosses a coin and you predict the outcome beforehand.",
)
async def coinflip(self, context: Context):
    buttons = Choice() -> None:
    """The bot tosses a coin and you predict the outcome beforehand."""
    

    embed = disnake.Embed(description="Choose heads or tails.", color=0x1F85DE)
    message = await context.send(embed=embed, view=buttons)
    await buttons.wait()
    result = random.choice(["heads", "tails"])
    if buttons.choice == result:

        embed = disnake.Embed(
            description=f"Correct guess. I flipped the coin to `{result}`.",
            color=0x00AB4C,
        )
    else:
        embed = disnake.Embed(
            description=f"Better luck next time. I flipped the coin to `{result}`.",
            color=0xE02B2B,
        )
    await message.edit(embed=embed, view=None)


def setup(bot: Bot) -> None:
    """Loading the coinflip cog."""
    bot.add_cog(Choice(bot))

