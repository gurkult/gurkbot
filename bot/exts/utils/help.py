import discord
from discord.ext import commands, menus
from discord.ext.commands import HelpCommand

import typing as t

from internal.context import Context

green = discord.from_rgb(50, 168, 82)


class HelpMenu(menus.Menu):
    """An interactive help menu."""

    def __init__(self, pages: t.List[discord.Embed], **kwargs):
        self.pages = pages
        self.page: int = 0
        self.title = pages[0].title
        super().__init__(**kwargs)

    def should_add_reactions(self):
        """Whether to add reactions to this menu session."""
        return len(self.pages) > 1

    async def send_initial_message(
        self, ctx: Context, channel: discord.abc.Messageable
    ):
        """Sends the initial message for the menu session."""
        return await ctx.reply(embed=self.pages[0])

    @menus.button("\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}")
    async def on_track_previous(self, payload: discord.RawReactionActionEvent):
        """A method to go back to the first page."""
        self.page = 0
        embed = self.pages[self.page]
        embed.title = self.title
        if embed is not self.message.embeds[0]:
            await self.message.edit(embed=embed)
        try:
            await self.message.remove_reaction(payload.emoji, self.ctx.author)
        except discord.Forbidden:
            pass

    @menus.button("\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}")
    async def on_rewind(self, payload: discord.RawReactionActionEvent):
        """A method to go to the previous page."""
        self.page -= 1
        if self.page < 0:
            self.page = 0
        else:
            embed = self.pages[self.page]
            embed.title = self.title
            if embed is not self.message.embeds[0]:
                await self.message.edit(embed=embed)
        try:
            await self.message.remove_reaction(payload.emoji, self.ctx.author)
        except discord.Forbidden:
            pass

    @menus.button("\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}")
    async def on_fast_forward(self, payload: discord.RawReactionActionEvent):
        """A method to go to the next page."""
        self.page += 1
        if self.page >= len(self.pages):
            self.page = len(self.pages) - 1
        else:
            embed = self.pages[self.page]
            embed.title = self.title
            if embed is not self.message.embeds[0]:
                await self.message.edit(embed=embed)
        try:
            await self.message.remove_reaction(payload.emoji, self.ctx.author)
        except discord.Forbidden:
            pass

    @menus.button("\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}")
    async def on_track_next(self, payload: discord.RawReactionActionEvent):
        """A method to go to the last page."""
        self.page = len(self.pages) - 1
        embed = self.pages[self.page]
        if embed is not self.message.embeds[0]:
            await self.message.edit(embed=embed)
        try:
            await self.message.remove_reaction(payload.emoji, self.ctx.author)
        except discord.Forbidden:
            pass

    @menus.button("\N{WASTEBASKET}")
    async def on_waste_bucket(self, payload: discord.RawReactionActionEvent):
        """A method to stop the help session."""
        self.stop()
        await self.message.delete()

    @classmethod
    def make_pages(cls, embed: discord.Embed, max_embeds: int, **options):
        """Make pages for the help menu session."""
        pages = []
        for page in range(0, len(embed.fields), max_embeds):
            embed1 = discord.Embed(
                title=embed.title, description=embed.description, colour=embed.colour
            )
            for field in embed.fields[page : page + max_embeds]:
                embed1.add_field(name=field.name, value=field.value, inline=False)
            pages.append(embed1)
        return cls(pages, **options)


class Help(HelpCommand):
    """Shows help for a command, group, or cog."""

    def get_command_signature(self, command: commands.Command):
        return f"{self.clean_prefix}{command.qualified_name} {command.signature}"

    async def send_bot_help(self, mapping):
        """Sends help for the bot."""
        embed = discord.Embed(
            title="Help",
            description="A list of commands for this bot.\n"
            "<> means mandatory while [] means optional.",
            colour=green,
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
        embed = discord.Embed(title=self.get_command_signature(command), colour=green)
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
            title=f"Help for the `{cog.qualified_name}` catagory.", colour=green
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
        embed = discord.Embed(
            title=f"Help for {group.name}.",
            description=group.help or "No help for this command.",
            colour=green,
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
        embed = discord.Embed(
            title="Error", description=error, colour=discord.Colour.red()
        )
        await self.context.send(embed=embed)
