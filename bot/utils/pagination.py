import typing as t

import discord
from discord.ext import commands, menus


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
        self, ctx: commands.Context, channel: discord.abc.Messageable
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
            for field in embed.fields[page: page + max_embeds]:
                embed1.add_field(name=field.name, value=field.value, inline=False)
            pages.append(embed1)
        return cls(pages, **options)
