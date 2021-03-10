import discord
from discord.ext import commands
from discord.ext.commands import Cog, HelpCommand

from bot.bot import Bot
from bot.utils.pagination import HelpMenu


class CustomHelpCommand(HelpCommand):
    """Shows help for a command, group, or cog."""

    def get_command_signature(self, command: commands.Command):
        return f"{self.clean_prefix}{command.qualified_name} {command.signature}"

    async def send_bot_help(self, mapping):
        """Sends help for the bot."""
        embed = discord.Embed(
            title="Help",
            description="A list of commands for this bot.\n"
            "<> means mandatory while [] means optional.",
            colour=0x87CEEB,
        )
        for cog, list_commands in mapping.items():

            list_commands = await self.filter_commands(list_commands, sort=True)

            command_signatures = [self.get_command_signature(c) for c in list_commands]

            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "Other Commands")
                embed.add_field(
                    name=cog_name, value="\n".join(command_signatures), inline=False
                )

        menu = HelpMenu.make_pages(embed, 5, clear_reactions_after=True)
        await menu.start(self.context, wait=True)

    async def send_command_help(self, command: commands.Command):
        embed = discord.Embed(
            title=self.get_command_signature(command), colour=0x87CEEB
        )
        embed.add_field(
            name="Help",
            value=command.help or "No description for this command.",
            inline=False,
        )

        if command.aliases:
            embed.add_field(
                name="Aliases", value=", ".join(f"`{x}`" for x in command.aliases)
            )

        await self.context.send(embed=embed)

    async def send_cog_help(self, cog: commands.Cog):
        embed = discord.Embed(
            title=f"Help for the `{cog.qualified_name}` catagory.", colour=0x87CEEB
        )
        for command in cog.get_commands():
            embed.add_field(
                name=command.name,
                value=command.help or "No description for this command",
                inline=False,
            )
        if len(embed.fields) >= 6:
            menu = HelpMenu.make_pages(embed, 5, remove_reactions_after=True)
            await menu.start(self.context, wait=True)
        else:
            await self.context.send(embed=embed)

    async def send_group_help(self, group: commands.Group):
        """Sends help for a specific group of commands."""
        embed = discord.Embed(
            title=f"Help for {group.name}.",
            description=group.help or "No help for this command.",
            colour=0x9B2335,
        )
        group_commands = ", ".join(f"`{command.name}`" for command in group.commands)
        embed.add_field(name=f"{group.name}'s subcommands", value=group_commands)

        if group.aliases:
            embed.add_field(name="Aliases", value=", ".join(group.aliases))

        embed.set_footer(
            text=f"Type {self.clean_prefix}{group.name} "
            "<command> to see info on each subcommand"
        )
        await self.context.send(embed=embed)

    async def send_error_message(self, error):
        """Sends an error message each time one occurs."""
        embed = discord.Embed(
            title="Error", description=error, colour=discord.Colour.red()
        )
        await self.context.send(embed=embed)


class Help(Cog):
    """Cog for the custom help command."""
    
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        bot.old_help_command = bot.help_command
        bot.help_command = CustomHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self) -> None:
        """Reset the help command when the cog is unloaded."""
        self.bot.help_command = self.old_help_command


def setup(bot: Bot) -> None:
    """Load the Help cog."""
    bot.add_cog(Help(bot))
