from typing import Optional

import discord
from bot.constants import Channels, Colours, Minecraft
from discord import Embed, TextChannel
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from loguru import logger
from mcstatus import MinecraftServer


class Gurkcraft(commands.Cog):
    """Gurkcraft Cog."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.server = MinecraftServer.lookup(Minecraft.server_address)
        self.gurkcraft: Optional[TextChannel] = None

        self.update_channel_description.start()

    @commands.command()
    async def mcstatus(self, ctx: commands.Context) -> None:
        """Collects data from minecraft server."""
        status = self.server.status()
        try:
            players = [user["name"] for user in status.raw["players"]["sample"]]
        except KeyError:
            players = ["None"]
        except OSError:
            await ctx.send(
                embed=Embed(
                    description="The server is currently offline.",
                    colour=Colours.soft_red,
                )
            )
            return

        embed = discord.Embed(title="Gurkcraft", color=Colours.green)
        embed.add_field(name="Server", value="mc.gurkult.com")
        embed.add_field(name="Server Latency", value=f"{status.latency}ms")
        embed.add_field(name="Gurkans Online", value=status.players.online)
        embed.add_field(name="Gurkans Connected", value=", ".join(players))
        await ctx.send(embed=embed)

    @tasks.loop(minutes=2)
    async def update_channel_description(self) -> None:
        """Collect informations about the server and update the description of the channel."""
        logger.debug("Updating topic of the #gurkcraft channel")

        if not self.gurkcraft:
            self.gurkcraft = await self.bot.fetch_channel(Channels.gurkcraft)

            if not self.gurkcraft:
                logger.warning(
                    f"Failed to retrieve #gurkcraft channel {Channels.gurkcraft}. Aborting."
                )
                return

        status = self.server.status()
        is_online = True
        try:
            players = [user["name"] for user in status.raw["players"]["sample"]]
        except KeyError:
            players = []
        except OSError:
            is_online = False

        if is_online:
            description = (
                "No players currently online. \n"
                if not players
                else (
                    f"{status.players.online} player{'s' if len(players) > 1 else ''} "
                    f"online: {', '.join(players)}. \n"
                )
                + f"Last server latency: {status.latency}ms"
            )
        else:
            description = "The server is currently offline :("

        await self.gurkcraft.edit(
            topic=f"Our gurkan Minecraft server. Join: {Minecraft.server_address} ! \n{description}"
        )


def setup(bot: Bot) -> None:
    """Loading the Gurkcraft cog."""
    bot.add_cog(Gurkcraft(bot))
