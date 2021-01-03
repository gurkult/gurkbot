from inspect import getsourcelines
from typing import Optional, Union

import discord
from aiohttp import ClientSession
from discord import Embed
from discord.ext.commands import Command


class Source:
    """Displays information about the bot's source code."""

    def __init__(
        self, http_session: ClientSession, bot_avatar: discord.asset.Asset
    ) -> None:
        self.http_session = http_session
        self.max_field_length = 500
        self.bot_avatar = bot_avatar

    async def inspect(self, cmd: Optional[Command]) -> Union[None, Embed]:
        """Display information and a GitHub link to the source code of a command."""
        if cmd is None:
            return

        module = cmd.module
        code_lines, start_line = getsourcelines(cmd.callback)
        url = (
            "<http://github.com/gurkult/gurkbot/blob/develop/"
            f'{"/".join(module.split("."))}.py#L{start_line}>\n'
        )
        source_code = "".join(code_lines)
        sanitized = source_code.replace("`", "\u200B`")
        if len(sanitized) > self.max_field_length:
            sanitized = (
                sanitized[: self.max_field_length]
                + "\n... (truncated - too many lines)"
            )

        embed = Embed(
            title="Gurkbot's Source Link", description=f"[Go to GitHub]({url})"
        )
        embed.add_field(name="Source Code", value=f"```python\n{sanitized}\n```")

        return embed
