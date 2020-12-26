import datetime
import json
import re
import urllib.parse
from io import BytesIO
from pathlib import Path
from typing import Optional

import aiohttp
from bot.bot import Bot
from discord import Embed, Message
from discord.ext import commands, tasks
from discord.ext.commands import Cog, CommandError, Context, command
from discord.utils import escape_mentions
from loguru import logger
from yaml import safe_load

from ._eval_helper import FormatOutput, Tio, get_raw, paste

WRAPPING = {
    "c": "#include <stdio.h>\nint main() {code}",
    "cpp": "#include <iostream>\nint main() {code}",
    "cs": "using System;class Program {static void Main(string[] args) {code}}",
    "java": "public class Main {public static void main(String[] args) {code}}",
    "rust": "fn main() {code}",
    "d": "import std.stdio; void main(){code}",
    "kotlin": "fun main(args: Array<String>) {code}",
}
QUICK_MAP = {
    "asm": "assembly",
    "c#": "cs",
    "c++": "cpp",
    "csharp": "cs",
    "f#": "fs",
    "fsharp": "fs",
    "js": "javascript",
    "nimrod": "nim",
    "py": "python",
    "q#": "qs",
    "rs": "rust",
    "sh": "bash",
}
SOFT_RED = 0xCD6D6D
GREEN = 0x1F8B4C


class Eval(Cog):
    """Safe evaluation of Code using Tio Run Api."""

    def __init__(self, bot: Bot):
        self.bot = bot
        with Path("bot/resources/eval/default_langs.yml").open(encoding="utf8") as file:
            self.default_languages = safe_load(file)
        self.languages_url = "https://tio.run/languages.json"
        self.update_languages.start()

    @tasks.loop(hours=5)
    async def update_languages(self) -> None:
        """Update list of languages supported by api every 5 hour."""
        logger.info("Updating List Of Languages")
        async with aiohttp.ClientSession() as client_session:
            async with client_session.get(self.languages_url) as response:
                if response.status != 200:
                    logger.warning(
                        f"Couldn't  reach languages.json (status code: {response.status})."
                    )
                languages = tuple(sorted(json.loads(await response.text())))
                self.languages = languages
        logger.info(
            f"Successfully Updated List Of Languages To Date: {datetime.datetime.now()}"
        )

    @command(
        help="""eval <language> [--wrapped] [--stats] <code>

            for command-line-options, compiler-flags and arguments you may
            add a line starting with this argument, and after a space add
            your options, flags or args.

            stats  - option displays more information on execution consumption
            wrapped  - allows you to not put main function in some languages

            <code> may be normal code, but also an attached file, or a link from  \
            [hastebin](https://hastebin.com) or [Github gist](https://gist.github.com)
            If you use a link, your command must end with this syntax: \
            `link=<link>` (no space around `=`)
            for instance : `!eval python link=https://hastebin.com/gurkbot.py`

            If the output exceeds 40 lines or Discord max message length, it will be put
            in a new hastebin and the link will be returned.
            """,
        brief="Execute code in a given programming language",
        name="eval",
        aliases=("e",),
    )
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def eval_command(
        self, ctx: Context, language: str, *, code: str = ""
    ) -> Optional[Message]:
        """
        Evaluate code, format it, and send the output to the corresponding channel.

        Return the bot response.
        """
        options = {"--stats": False, "--wrapped": False}
        lang = language.strip("`").lower()
        options_amount = len(options)

        # Setting options and removing them from the beginning of the command
        # options may be separated by any single whitespace, which we keep in the list
        code = re.split(r"(\s)", code, maxsplit=options_amount)
        for option in options:
            if option in code[: options_amount * 2]:
                options[option] = True
                i = code.index(option)
                code.pop(i)
                code.pop(i)  # Remove following whitespace character
        code = "".join(code)

        compiler_flags = []
        command_line_options = []
        args = []
        inputs = []

        lines = code.split("\n")
        code = []
        for line in lines:
            if line.startswith("input "):
                inputs.append(" ".join(line.split(" ")[1:]).strip("`"))
            elif line.startswith("compiler-flags "):
                compiler_flags.extend(line[15:].strip("`").split(" "))
            elif line.startswith("command-line-options "):
                command_line_options.extend(line[21:].strip("`").split(" "))
            elif line.startswith("arguments "):
                args.extend(line[10:].strip("`").split(" "))
            else:
                code.append(line)

        inputs = "\n".join(inputs)
        code = "\n".join(code)
        text = None

        async with ctx.typing():
            if ctx.message.attachments:
                # Code in file
                file = ctx.message.attachments[0]
                if file.size > 20000:
                    await ctx.send("File must be smaller than 20 kio.")
                    logger.info("Exiting | File bigger than 20 kio.")
                    return
                buffer = BytesIO()
                await ctx.message.attachments[0].save(buffer)
                text = buffer.read().decode("utf-8")

            elif code.split(" ")[-1].startswith("link="):
                # Code in a paste service (gist or a hastebin link)
                base_url = urllib.parse.quote_plus(
                    code.split(" ")[-1][5:].strip("/"), safe=";/?:@&=$,><-[]"
                )
                url = get_raw(base_url)

                async with aiohttp.ClientSession() as client_session:
                    async with client_session.get(url) as response:
                        if response.status == 404:
                            await ctx.send("Nothing found. Check your link")
                            logger.info("Exiting | Nothing found in link.")
                            return
                        elif response.status != 200:
                            logger.warning(
                                f"An error occurred | status code: "
                                f"{response.status} | on request by: {ctx.author}"
                            )
                            await ctx.send(
                                f"An error occurred (status code: {response.status}). "
                                f"Retry later."
                            )
                            return
                        text = await response.text()

            elif code.strip("`"):
                # Code in message
                text = code.strip("`")
                first_line = text.splitlines()[0]
                if re.fullmatch(r"( |[0-9A-z]*)\b", first_line):
                    text = text[len(first_line) + 1 :]

            if text is None:
                # Ensures code isn't empty after removing options
                raise commands.MissingRequiredArgument(ctx.command.clean_params["code"])

            if lang in QUICK_MAP:
                lang = QUICK_MAP[lang]
            if lang in self.default_languages:
                lang = self.default_languages[lang]
            if lang not in self.languages:
                if not escape_mentions(lang):
                    embed = Embed(
                        title="MissingRequiredArgument",
                        description=f"Missing Argument Language.\n\nUsage:\n"
                        f"```{ctx.prefix}{ctx.command} {ctx.command.signature}```",
                        color=SOFT_RED,
                    )
                else:
                    embed = Embed(
                        title="Language Not Supported",
                        description=f"Your language was invalid: {lang}\n"
                        f"All Supported languages: [here](https://tio.run)\n\nUsage:\n"
                        f"```{ctx.prefix}{ctx.command} {ctx.command.signature}```",
                        color=SOFT_RED,
                    )
                await ctx.send(embed=embed)
                logger.info("Exiting | Language not found.")
                return

            if options["--wrapped"]:
                if not (
                    any(map(lambda x: lang.split("-")[0] == x, WRAPPING))
                ) or lang in ("cs-mono-shell", "cs-csi"):
                    await ctx.send(f"`{lang}` cannot be wrapped")
                    return

                for beginning in WRAPPING:
                    if lang.split("-")[0] == beginning:
                        text = WRAPPING[beginning].replace("code", text)
                        break

            tio = Tio(lang, text, inputs, compiler_flags, command_line_options, args)
            result = await tio.get_result()
            result = result.rstrip("\n")

            if not options["--stats"]:
                try:
                    start, end = result.rindex("Real time: "), result.rindex(
                        "%\nExit code: "
                    )
                    result = result[:start] + result[end + 2 :]
                except ValueError:
                    pass

            if len(result) > 1991 or result.count("\n") > 40:
                output = await paste(result)

                format_output = FormatOutput(language=lang)
                embed = format_output.format_hastebin_output(output, result)

                await ctx.send(content=f"{ctx.author.mention}", embed=embed)
                logger.info("Result Sent.")
                return

            format_output = FormatOutput(language=lang)
            embed = format_output.format_message_output(result)

            await ctx.send(content=f"{ctx.author.mention}", embed=embed)
            logger.info("Result Sent.")

    @eval_command.error
    async def eval_command_error(self, ctx: Context, error: CommandError) -> None:
        """A error handler for Eval Command."""
        if isinstance(error, commands.MissingRequiredArgument):
            embed = Embed(
                title="MissingRequiredArgument",
                description=f"Your input was invalid: {error}\n\nUsage:\n"
                f"```{ctx.prefix}{ctx.command} {ctx.command.signature}```",
                color=SOFT_RED,
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.CommandOnCooldown):
            embed = Embed(
                title="Cooldown",
                description=f"You’re on a cooldown for this command. Please "
                f"wait **{int(error.retry_after)}s** "
                "until you use it again.",
                color=SOFT_RED,
            )
            await ctx.send(embed=embed)
            return


def setup(bot: Bot) -> None:
    """Load the Eval cog."""
    bot.add_cog(Eval(bot))
