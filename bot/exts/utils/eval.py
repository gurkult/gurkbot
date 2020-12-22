import datetime
import json
import re
import urllib.parse
from io import BytesIO
from pathlib import Path
from typing import Optional

import aiohttp
import discord
from bot.bot import Bot
from discord import Message
from discord.ext import commands, tasks
from discord.ext.commands import Cog, Context, command
from discord.utils import escape_mentions
from loguru import logger
from yaml import safe_load as yaml_load

from ._eval_helper import Tio, get_raw, paste


class Eval(Cog):
    """Safe evaluation of Code using Tio Run Api."""

    def __init__(self, bot: Bot):
        self.bot = bot
        with Path("bot/resources/default_langs.yml").open(encoding="utf8") as file:
            self.default = yaml_load(file)
        self.languages_url = 'https://tio.run/languages.json'
        self.languages = None
        self.update_languages.start()

    @tasks.loop(hours=5)
    async def update_languages(self) -> None:
        """Update list of languages supported by api every 1 hour."""
        logger.info("Updating List Of Languages")
        async with aiohttp.ClientSession() as client_session:
            async with client_session.get(self.languages_url) as response:
                if response.status != 200:
                    print(f"Couldn't reach languages.json (status code: {response.status}).")
                languages = tuple(sorted(json.loads(await response.text())))

                # Rare reassignments
                if self.languages != languages:
                    self.languages = languages
        logger.info(f"Successfully Updated List Of Languages To Date: {datetime.datetime.now()}")

    wrapping = {
        'c': '#include <stdio.h>\nint main() {code}',
        'cpp': '#include <iostream>\nint main() {code}',
        'cs': 'using System;class Program {static void Main(string[] args) {code}}',
        'java': 'public class Main {public static void main(String[] args) {code}}',
        'rust': 'fn main() {code}',
        'd': 'import std.stdio; void main(){code}',
        'kotlin': 'fun main(args: Array<String>) {code}'
    }

    @command(
        help='''eval <language> [--wrapped] [--stats] <code>

            for command-line-options, compiler-flags and arguments you may
            add a line starting with this argument, and after a space add
            your options, flags or args.

            stats option displays more information on execution consumption
            wrapped allows you to not put main function in some languages

            <code> may be normal code, but also an attached file, or a link from  \
            [hastebin](https://hastebin.com) or [Github gist](https://gist.github.com)
            If you use a link, your command must end with this syntax: \
            `link=<link>` (no space around `=`)
            for instance : `!eval python link=https://hastebin.com/gurkbot.py`

            If the output exceeds 40 lines or Discord max message length, it will be put
            in a new hastebin and the link will be returned.
            ''',
        brief='Execute code in a given programming language',
        name="eval",
        aliases=("e",)
    )
    async def eval_command(self, ctx: Context, language: str, *, code: str = '') -> Optional[Message]:
        """
        Evaluate code, format it, and send the output to the corresponding channel.

        Return the bot response.
        """
        logger.info(f"Received code from {ctx.author} for evaluation:\n{code}")

        options = {
            '--stats': False,
            '--wrapped': False
        }
        lang = language.strip('`').lower()
        options_amount = len(options)

        # Setting options and removing them from the beginning of the command
        # options may be separated by any single whitespace, which we keep in the list
        code = re.split(r'(\s)', code, maxsplit=options_amount)

        for option in options:
            if option in code[:options_amount * 2]:
                options[option] = True
                i = code.index(option)
                code.pop(i)
                code.pop(i)  # remove following whitespace character

        code = ''.join(code)

        compiler_flags = []
        command_line_options = []
        args = []
        inputs = []

        lines = code.split('\n')
        code = []
        for line in lines:
            if line.startswith('input '):
                inputs.append(' '.join(line.split(' ')[1:]).strip('`'))
            elif line.startswith('compiler-flags '):
                compiler_flags.extend(line[15:].strip('`').split(' '))
            elif line.startswith('command-line-options '):
                command_line_options.extend(line[21:].strip('`').split(' '))
            elif line.startswith('arguments '):
                args.extend(line[10:].strip('`').split(' '))
            else:
                code.append(line)

        inputs = '\n'.join(inputs)
        code = '\n'.join(code)
        text = None

        async with ctx.typing():
            if ctx.message.attachments:
                # Code in file
                file = ctx.message.attachments[0]
                if file.size > 20000:
                    return await ctx.send("File must be smaller than 20 kio.")
                buffer = BytesIO()
                await ctx.message.attachments[0].save(buffer)
                text = buffer.read().decode('utf-8')

            elif code.split(' ')[-1].startswith('link='):
                # Code in a webpage
                base_url = urllib.parse.quote_plus(code.split(' ')[-1][5:].strip('/'), safe=';/?:@&=$,><-[]')
                url = get_raw(base_url)

                async with aiohttp.ClientSession() as client_session:
                    async with client_session.get(url) as response:
                        if response.status == 404:
                            return await ctx.send('Nothing found. Check your link')
                        elif response.status != 200:
                            return await ctx.send(f'An error occurred (status code: {response.status}). '
                                                  f'Retry later.')
                        text = await response.text()
                        if len(text) > 20000:
                            return await ctx.send('Code must be shorter than 20,000 characters.')

            elif code.strip('`'):
                # Code in message
                text = code.strip('`')
                first_line = text.splitlines()[0]
                if re.fullmatch(r'( |[0-9A-z]*)\b', first_line):
                    text = text[len(first_line) + 1:]

            if text is None:
                # Ensures code isn't empty after removing options
                raise commands.MissingRequiredArgument(ctx.command.clean_params['code'])


            # common identifiers, also used in highlight.js and thus discord codeblocks
            quick_map = {
                'asm': 'assembly',
                'c#': 'cs',
                'c++': 'cpp',
                'csharp': 'cs',
                'f#': 'fs',
                'fsharp': 'fs',
                'js': 'javascript',
                'nimrod': 'nim',
                'py': 'python',
                'q#': 'qs',
                'rs': 'rust',
                'sh': 'bash',
            }

            if lang in quick_map:
                lang = quick_map[lang]

            if lang in self.default:
                lang = self.default[lang]
            if lang not in self.languages:
                matches = '\n'.join([language for language in self.languages if lang in language][:10])
                lang = escape_mentions(lang)
                message = f"`{lang}` not available."
                if matches:
                    message += f" Did you mean:\n{matches}"

                return await ctx.send(message)

            if options['--wrapped']:
                if not (any(map(lambda x: lang.split('-')[0] == x, self.wrapping))) or lang in (
                        'cs-mono-shell', 'cs-csi'):
                    return await ctx.send(f'`{lang}` cannot be wrapped')

                for beginning in self.wrapping:
                    if lang.split('-')[0] == beginning:
                        text = self.wrapping[beginning].replace('code', text)
                        break

            tio = Tio(lang, text, compiler_flags=compiler_flags, inputs=inputs,
                      command_line_options=command_line_options,
                      args=args)

            result = await tio.send()

            if not options['--stats']:
                try:
                    start = result.rindex("Real time: ")
                    end = result.rindex("%\nExit code: ")
                    result = result[:start] + result[end + 2:]
                except ValueError:
                    # Too much output removes this markers
                    pass

            if len(result) > 1991 or result.count('\n') > 40:
                # If it exceeds 2000 characters (Discord longest message), counting ` and ph\n characters
                # Or if it floods with more than 40 lines
                # Create a hastebin and send it back
                link = await paste(result)

                if link is None:
                    return await ctx.send("Your output was too long, but "
                                          "I couldn't make an online bin out of it")
                return await ctx.send(
                    f'Output was too long (more than 2000 characters or 40 lines) '
                    f'so I put it here: {link}')

            logger.info("Formatting output...")

            zero = '\N{zero width space}'
            result = re.sub('```', f'{zero}`{zero}`{zero}`{zero}', result)

            result, exit_code = result.split('Exit code: ')

            icon = ":white_check_mark:" if exit_code == '0' else ":warning:"
            msg = f"Your eval job has completed with return code {exit_code}"

            logger.info(f"{ctx.author}'s job had a return code of {exit_code}")
            await ctx.send(f'{ctx.author.mention} {icon} {msg}.\n\n```{lang}\n{result}```')


def setup(bot: Bot) -> None:
    """Load the Eval cog."""
    bot.add_cog(Eval(bot))
