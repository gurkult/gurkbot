import disnake
from disnake.ext import commands
from disnake.utils import get

from bot.bot import Bot
from bot.constants import Roles
from bot.utils.is_gurkan import gurkan_check


class MakeGurkan(commands.Cog):
    """Makes sure that only members with gurkan names have the gurkan role."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(
        self, before: disnake.Member, after: disnake.Member
    ) -> None:
        """
        Adds/Removes the gurkan role on member update.

        When the member updates their nickname or username, this function will check if member is
        classified to be a gurkan or not.
        """
        if after.bot:
            return
        if before.display_name != after.display_name:
            role = get(after.guild.roles, id=Roles.gurkans)
            if gurkan_check(after.display_name):
                if role not in after.roles:
                    await after.add_roles(role)
            else:
                if role in after.roles:
                    await after.remove_roles(role)

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member) -> None:
        """Adds the gurkan role to new members who are classified as gurkans."""
        if member.bot:
            return
        role = get(member.guild.roles, id=Roles.gurkans)
        if gurkan_check(member.display_name):
            await member.add_roles(role)


def setup(bot: commands.Bot) -> None:
    """Load the Cog."""
    bot.add_cog(MakeGurkan(bot))
