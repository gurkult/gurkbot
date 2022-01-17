from typing import Optional

import disnake
from disnake import Embed, TextChannel
from disnake.ext import commands, tasks
from disnake.ext.commands import Bot
from loguru import logger
from mcstatus import MinecraftServer

from bot.constants import Channels, Colours, Minecraft

CHAT_HEADER = "Our gurkan Minecraft server. Join: {Minecraft.server_address} ! \n"
RELAY_HEADER = "The live chat of our gurkan Minecraft server. \n"


def _extract_users(status: dict) -> list:
    """Extract the list of users connected to the server."""
    try:
        return [user["name"] for user in status.raw["players"]["sample"]]
    except KeyError:
        return []


class Gurkcraft(commands.Cog):
    """Gurkcraft Cog."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.server = MinecraftServer.lookup(Minecraft.server_address)
        self.gurkcraft: Optional[TextChannel] = None
        self.gurkcraft_relay: Optional[TextChannel] = None

        self.update_channel_description.start()

    @commands.command()
    async def mcstatus(self, ctx: commands.Context) -> None:
        """Collects data from minecraft server."""
        try:
            status = self.server.status()
        except OSError:
            await ctx.send(
                embed=Embed(
                    description="The server is currently offline.",
                    colour=Colours.soft_red,
                )
            )
            return
        players = _extract_users(status)

        embed = disnake.Embed(title="Gurkcraft", color=Colours.green)
        embed.add_field(name="Server", value="mc.gurkult.com")
        embed.add_field(name="Server Latency", value=f"{status.latency}ms")
        embed.add_field(name="Gurkans Online", value=status.players.online)
        embed.add_field(
            name="Gurkans Connected", value=", ".join(players) if players else "None"
        )
        await ctx.send(embed=embed)

    @tasks.loop(minutes=5)
    async def update_channel_description(self) -> None:
        """Collect information about the server and update the description of the channel."""
        logger.debug("Updating topic of the #gurkcraft and #gurkcraft-relay channel")

        if not self.gurkcraft:
            self.gurkcraft = await self.bot.fetch_channel(Channels.gurkcraft)

            if not self.gurkcraft:
                logger.warning(
                    f"Failed to retrieve #gurkcraft channel {Channels.gurkcraft}. Aborting."
                )
                return
        if not self.gurkcraft_relay:
            self.gurkcraft_relay = await self.bot.fetch_channel(
                Channels.gurkcraft_relay
            )

            if not self.gurkcraft_relay:
                logger.warning(
                    f"Failed to retrieve #gurkcraft_relay channel {Channels.gurkcraft_relay}. Aborting."
                )
                return

        is_online = True
        try:
            status = self.server.status()
            players = _extract_users(status)
        except OSError:
            is_online = False
            players = []

        if is_online:
            description = (
                "No players currently online."
                if not players
                else (
                    f"{status.players.online} player{'s' if len(players) > 1 else ''} "
                    f"online: {', '.join(players)}."
                )
            )
        else:
            description = "The server is currently offline :("

        await self.gurkcraft.edit(topic=CHAT_HEADER + description)
        await self.gurkcraft_relay.edit(topic=RELAY_HEADER + description)


def setup(bot: Bot) -> None:
    """Loading the Gurkcraft cog."""
    bot.add_cog(Gurkcraft(bot))
