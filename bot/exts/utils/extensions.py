import typing as t

import bot.utils.extension as extension
from bot.constants import Roles

from discord.ext import commands
from discord.ext.commands.errors import (
    BadArgument,
    ExtensionAlreadyLoaded,
    ExtensionNotLoaded,
)

from loguru import logger


UNLOAD_BLACKLIST = ["bot.exts.utils.extensions"]


class Extension(commands.Converter):
    """
    Qualifying the name of the extension and make sure it exists.

    If it does then try to get its path.
    The * value bypass this when used with the reload command. 
    """

    async def convert(self, ctx: commands.Context, argument: str) -> str:
        """Make sure the extension exists and get its full path."""
        # special value to reload all extension
        if '*' == argument or '**' in argument:
            return argument
        
        if argument in extension.EXTENSIONS:
            return argument
        
        argument = argument.lower()

        matches = []
        if all(
            argument != check_extension[len(check_extension) - 1]
            for check_extension in [ext.split(".") for ext in extension.EXTENSIONS]
        ):
            raise BadArgument(f"{argument} is not an extension name. \n")

        for ext in extension.EXTENSIONS:
            check_extension = ext.split(".")
            if argument == check_extension[len(check_extension) - 1]:
                matches.append("".join(ext))
        
        return " ".join(matches)


class Extensions(commands.Cog):
    """Commands for extension management."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.group(
        name="extensions",
        aliases=["ext", "exts", "cog"],
        invoke_without_command=True,
    )
    async def extension_group(self, ctx: commands.Context) -> None:
        """Load, unload, reload, and list loaded extensions."""
        await ctx.send_help(ctx.command)

    @extension_group.command(name="load", aliases=["l"])
    async def loading(self, ctx: commands.Context, *extensions: Extension) -> None:
        """Loads the given extensions.
        If `*` is provided as the extension then loads every single extension.
        To reload the extension of an entire folder, `**` must be before the folder name.
        """
        if not extensions:
            await ctx.send_help(ctx.command)
            return
                        
        if '*' in extensions:
            extensions = extension.EXTENSIONS

        messages = self.manage("load", extensions)
        await ctx.channel.send(messages)

    @extension_group.command(name="reload", aliases=["rl"])
    async def reloading(self, ctx: commands.Cog, *extensions: Extension) -> None:
        """
        Reloads the given extensions.
        If `*` is provided as the extension then reloads all the extensions.
        To reload the extension of an entire folder, `**` must be before the folder name.
        """
        if not extensions:
            await ctx.send_help(ctx.command)
            return
        
        if '*' in extensions:
            extensions = extension.EXTENSIONS

        messages = self.manage("reload", extensions)
        await ctx.channel.send(messages)

    @extension_group.command(name="unload", aliases=["ul"])
    async def unloading(self, ctx: commands.Cog, *extensions: Extension) -> None:
        """
        Unloads the given extensions.
        If `*` is provided as the extension then unloads every all the extensions.
        To reload the extension of an entire folder, `**` must be before the folder name.
        """
        if not extensions:
            await ctx.send_help(ctx.command)
            return
        
        if '*' in extensions:
            extensions = [  ext for ext in extension.EXTENSIONS 
                            if ext not in UNLOAD_BLACKLIST
                        ]

        blacklists = [
            blacklisted_extesnion
            for blacklisted_extesnion in extensions
            if blacklisted_extesnion in UNLOAD_BLACKLIST
        ]
        
        if blacklists:
            await ctx.channel.send(
                f":x: `{' ,'.join(blacklists)}` extensions can not be unloaded"
            )
            logger.info(
                f"{str(ctx.author)} Tried to unload blacklisted extension"
                f"{', '.join(blacklists)}"
            )
            return

        messages = self.manage("unload", extensions)
        await ctx.channel.send(messages)
    

    def manage(
        self,
        action: str,
        extensions: t.Tuple[str],
    ) -> str:
        """Apply an action to the provided extension/extensions."""
        if not extensions:
            raise ValueError("Extension not provided.")

        actions = {
            "load": self.bot.load_extension,
            "unload": self.bot.unload_extension,
            "reload": self.bot.reload_extension,
        }

        if action not in actions:
            raise BadArgument(
                f"{action} could not be found."
            )

        folders = [
            folder[folder.index('*')+2:]
            for folder in extensions
            if '**' in folder
        ]
        extensions_ = []

        for folder in folders:
            for ext in extension.EXTENSIONS:
                ext_folder = ext.split('.')[ext.split('.').index('exts')+1]
                if (
                    folder == ext_folder
                    and action == 'unload'
                    and ext not in UNLOAD_BLACKLIST
                ):

                    extensions_.append(ext)

        extensions = [ext for ext in extensions if '**' not in ext] + extensions_
        message = ""
        for ext in extensions:
            try:
                actions[action](ext)
            except ExtensionAlreadyLoaded:
                message += f":x: `{ext}` Already loaded. \n"
                logger.debug(f"Failed to {action} on {ext}" f"{ext} Already loaded.")
            except ExtensionNotLoaded:
                message += f":x: `{ext}` Not loaded. \n"
                logger.debug(
                    f"Failed to {action} on {ext}." f"{ext} Already not loaded."
                )
            else:
                message += f":ok_hand: Successfully {action}ed: `{ext}`. \n"

        return message

    async def cog_check(self, ctx):
        """Only allow steering councila and lords to use the extensions command"""
        return await commands.has_any_role(
            Roles.steering_council, Roles.lords
        ).predicate(ctx)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Extensions(bot))