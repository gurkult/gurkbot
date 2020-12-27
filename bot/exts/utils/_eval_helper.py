import re
import urllib.parse
import zlib
from functools import partial
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union

import aiohttp
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Context
from loguru import logger

to_bytes = partial(bytes, encoding="utf-8")


def _to_tio_string(couple: tuple) -> bytes:
    """
    Return a tio api compatible string.

    For example:
    (language) bash -> b'Vlang\x001\x00bash\x00'
    (code) echo "bash" -> b'F.code.tio\x0019\x00echo "bash"\n\x00'
    """
    name, obj = couple
    if not obj:
        return b""
    elif isinstance(obj, list):
        content = [f"V{name}", str(len(obj))] + obj
        return to_bytes("\x00".join(content) + "\x00")
    else:
        return to_bytes(f"F{name}\x00{len(to_bytes(obj))}\x00{obj}\x00")


class Tio:
    """Helper class for eval command."""

    def __init__(
        self,
        language: str,
        code: str,
        inputs: str = "",
        compiler_flags: Optional[list] = None,
        command_line_options: Optional[list] = None,
        args: Optional[list] = None,
    ) -> None:
        if args is None:
            args = []
        if command_line_options is None:
            command_line_options = []
        if compiler_flags is None:
            compiler_flags = []
        self.backend = "https://tio.run/cgi-bin/run/api/"
        self.json = "https://tio.run/languages.json"

        strings = {
            "lang": [language],
            ".code.tio": code,
            ".input.tio": inputs,
            "TIO_CFLAGS": compiler_flags,
            "TIO_OPTIONS": command_line_options,
            "args": args,
        }

        bytes_ = (
            b"".join(
                map(
                    _to_tio_string,  # func
                    zip(strings.keys(), strings.values()),  # iterables
                )
            )
            + b"R"
        )

        # This returns a DEFLATE-compressed byte-string, which is what the API requires
        self.request = zlib.compress(bytes_, 9)[2:-4]

    async def get_result(self) -> str:
        """Send Request to Tio Run API And Get Result."""
        async with aiohttp.ClientSession() as client_session:
            async with client_session.post(self.backend, data=self.request) as res:
                if res.status != 200:
                    logger.warning(
                        f"HttpProcessingError while getting result of code from tio api with "
                        f"status code: {res.status}"
                    )

                data = await res.read()
                data = data.decode("utf-8")
                return data.replace(data[:16], "")  # remove token


class EvalHelper:
    """Eval Helper class."""

    def __init__(self, language: str) -> None:
        self.lang = language.strip("`").lower()
        self.authorized = (
            "https://hastebin.com",
            "https://gist.github.com",
            "https://gist.githubusercontent.com",
        )
        self.max_file_size = 20000
        self.truncated_error = "The output exceeded 128 KiB and was truncated."
        self.hastebin_link = "https://hastebin.com"
        self.bin_link = "https://bin.drlazor.be/"

    async def parse(
        self, code: str
    ) -> Tuple[
        str, str, str, Dict[Union[str, Any], bool], List[str], List[str], List[str]
    ]:
        """Returned parsed data."""
        options = {"--stats": False, "--wrapped": False}
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
        return (
            inputs,
            code,
            self.lang,
            options,
            compiler_flags,
            command_line_options,
            args,
        )

    async def code_from_attachments(self, ctx: Context) -> Optional[str]:
        """Code in file."""
        file = ctx.message.attachments[0]
        if file.size > self.max_file_size:
            await ctx.send("File must be smaller than 20 kio.")
            logger.info("Exiting | File bigger than 20 kio.")
            return
        buffer = BytesIO()
        await ctx.message.attachments[0].save(buffer)
        text = buffer.read().decode("utf-8")
        return text

    async def code_from_url(self, ctx: Context, code: str) -> Optional[str]:
        """Get code from url."""
        base_url = urllib.parse.quote_plus(
            code.split(" ")[-1][5:].strip("/"), safe=";/?:@&=$,><-[]"
        )
        print(base_url)
        url = self.get_raw(base_url)
        print(url)

        async with aiohttp.ClientSession() as client_session:
            async with client_session.get(url) as response:
                print(response.status)
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
                return text

    async def paste(self, text: str) -> Union[str, dict]:
        """Upload the eval output to a paste service and return a URL to it if successful."""
        logger.info("Uploading full output to paste service...")
        result = dict()
        text, exit_code = text.split("Exit code: ")
        if self.truncated_error in exit_code:
            exit_code = exit_code.replace(self.truncated_error, "")
        result["exit_code"] = exit_code
        result["icon"] = ":white_check_mark:" if exit_code == "0" else ":warning:"

        async with aiohttp.ClientSession() as session:
            post = await session.post(f"{self.hastebin_link}/documents", data=text)
            if post.status == 200:
                response = await post.text()
                result["link"] = f"{self.hastebin_link}{response[8:-2]}"
                return result

            # Rollback bin
            post = await session.post(f"{self.bin_link}", data={"val": text})
            if post.status == 200:
                result["link"] = post.url
                return result

    def get_raw(self, link: str) -> str:
        """Returns the url to raw text version of certain pastebin services."""
        link = link.strip("<>/")  # Allow for no-embed links

        if not any(link.startswith(url) for url in self.authorized):
            raise commands.BadArgument(
                message=f"Only links from the following domains are accepted: {', '.join(self.authorized)}. "
                f"(Starting with 'https')."
            )

        domain = link.split("/")[2]

        if domain == "hastebin.com":
            if "/raw/" in link:
                return link
            token = link.split("/")[-1]
            if "." in token:
                token = token[: token.rfind(".")]  # removes extension
            return f"{self.hastebin_link}/raw/{token}"
        else:
            # Github uses redirection so raw -> user content and no raw -> normal
            # We still need to ensure we get a raw version after this potential redirection
            if "/raw" in link:
                return link
            return link + "/raw"


class FormatOutput:
    """Format Output sent by the Tio.run Api and return embed."""

    def __init__(self, language: str) -> None:
        self.language = language
        self.GREEN = 0x1F8B4C
        self.max_lines = 11
        self.max_output_length = 500

    @staticmethod
    def get_icon(exit_code: str) -> str:
        """Get icon depending on what is the exit code."""
        return ":white_check_mark:" if exit_code == "0" else ":warning:"

    def embed_helper(self, description: str, field: str) -> Embed:
        """Embed helper function."""
        embed = Embed(title="Eval Results", colour=self.GREEN, description=description)
        embed.add_field(
            name="Output",
            value=field,
        )
        return embed

    def format_hastebin_output(self, output: dict, result: str) -> Embed:
        """
        Format Hastebin Output.

        Helper function to format output to return embed if the result,
        is more than 1991 characters or 40 lines.
        """
        logger.info("Formatting hastebin output...")
        if result.count("\n") > 40:
            result = [
                f"{i:02d} | {line}" for i, line in enumerate(result.split("\n"), 1)
            ]
            result = result[: self.max_lines]  # Limiting to only 11 lines
            program_output = "\n".join(result) + "\n... (truncated - too many lines)"

        elif len(result) > 1991:
            program_output = (
                result[: self.max_output_length] + "\n... (truncated - too long)"
            )

        embed = self.embed_helper(
            description=f"{output['icon']} Your {self.language} eval job has "
            f"completed with return code `{output['exit_code']}`",
            field=f"```\n{program_output}```\nYou can find the complete "
            f"output [here]({output['link']})",
        )

        logger.info("Output Formatted")
        return embed

    def format_code_output(self, result: str) -> Embed:
        """
        Format Code Output.

        Helper function to format output to return embed if the result
        is less than 1991 characters or 40 lines.
        """
        logger.info("Formatting message output...")

        zero = "\N{zero width space}"
        result = re.sub("```", f"{zero}`{zero}`{zero}`{zero}", result)
        result, exit_code = result.split("Exit code: ")
        icon = self.get_icon(exit_code)
        result = result.rstrip("\n")
        lines = result.count("\n")

        if lines > 0:
            result = [
                f"{i:02d} | {line}" for i, line in enumerate(result.split("\n"), 1)
            ]
            result = result[: self.max_lines]  # Limiting to only 11 lines
            result = "\n".join(result)
        if lines > self.max_lines - 1:
            if len(result) >= 1000:
                result = f"{result[:self.max_output_length]}\n... (truncated - too long, too many lines)"
            else:
                result = f"{result}\n... (truncated - too many lines)"
        elif len(result) >= 1000:
            result = f"{result[:self.max_output_length]}\n... (truncated - too long)"

        embed = self.embed_helper(
            description=f"{icon} Your {self.language} eval job has completed with return code `{exit_code}`.",
            field=f"```\n{'[No output]' if result == '' else result}```",
        )

        logger.info("Output Formatted")
        return embed
