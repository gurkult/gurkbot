import re
from inspect import getsourcelines
from textwrap import dedent
from typing import Optional

import disnake
from aiohttp import ClientSession
from disnake.ext.commands import Command

from bot import constants

doc_reg_class = r'("""|\'\'\')([\s\S]*?)(\1\s*)'


class Source:
    """Displays information about the bot's source code."""

    def __init__(
        self, http_session: ClientSession, bot_avatar: disnake.asset.Asset
    ) -> None:
        self.http_session = http_session
        self.MAX_FIELD_LENGTH = 500
        self.bot_avatar = bot_avatar

    async def inspect(self, cmd: Optional[Command]) -> Optional[disnake.Embed]:
        """Display information and a GitHub link to the source code of a command."""
        if cmd is None:
            return

        module = cmd.module
        code_lines, start_line = getsourcelines(cmd.callback)
        url = (
            f"<{constants.BOT_REPO_URL}/tree/main/"
            f'{"/".join(module.split("."))}.py#L{start_line}>\n'
        )

        source_code = "".join(code_lines)
        sanitized = source_code.replace("`", "\u200B`")
        sanitized = re.sub(doc_reg_class, "", sanitized)
        # The help argument of commands.command gets changed to `help=`
        sanitized = sanitized.replace("help=", 'help=""')

        # Remove the extra indentation in the code.
        sanitized = dedent(sanitized)

        if len(sanitized) > self.MAX_FIELD_LENGTH:
            sanitized = (
                sanitized[: self.MAX_FIELD_LENGTH]
                + "\n... (truncated - too many lines)"
            )

        embed = disnake.Embed(title="Gurkbot's Source Link", description=f"{url}")
        embed.add_field(
            name="Source Code Snippet", value=f"```python\n{sanitized}\n```"
        )

        return embed
