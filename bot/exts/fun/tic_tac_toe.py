import asyncio
import random
import typing as t
from functools import partial

import discord
from discord.ext.commands import Cog, Context, check, group, guild_only

from bot.bot import Bot
from bot.constants import Emojis

CROSS_EMOJI = "\u274e"
HAND_RAISED_EMOJI = "\U0001f64b"
EMOJI_TOKENS = (Emojis.cucumber, Emojis.watermelon)


def check_win(board: t.Dict[int, str]) -> bool:
    """Check from board, is any player won game."""
    return any(
        (
            # Horizontal
            board[1] == board[2] == board[3],
            board[4] == board[5] == board[6],
            board[7] == board[8] == board[9],
            # Vertical
            board[1] == board[4] == board[7],
            board[2] == board[5] == board[8],
            board[3] == board[6] == board[9],
            # Diagonal
            board[1] == board[5] == board[9],
            board[3] == board[5] == board[7],
        )
    )


class Player:
    """Class that contains information about player and functions that interact with player."""

    def __init__(self, user: discord.User, ctx: Context, symbol: str):
        self.user = user
        self.ctx = ctx
        self.symbol = symbol

    async def get_move(
            self, board: t.Dict[int, str], msg: discord.Message
    ) -> t.Tuple[bool, t.Optional[int], bool]:
        """
        Get move from user.
        Return is timeout reached
        and position of field what user will fill when timeout don't reach
        and whether the game was abandoned or not.
        """

        def check_for_move(r: discord.Reaction, u: discord.User) -> bool:
            """Check does user who reacted is user who we want, message is board and emoji is in board values or is
            CROSS_EMOJI. """
            return (
                    u.id == self.user.id
                    and msg.id == r.message.id
                    and (str(r.emoji) == CROSS_EMOJI or r.emoji in Emojis.number_emojis.values())
            )

        try:
            react, _ = await self.ctx.bot.wait_for(
                "reaction_add", timeout=60, check=check_for_move
            )
        except asyncio.TimeoutError:
            return True, None, False
        else:
            if str(react.emoji) == CROSS_EMOJI:
                return False, None, True

            return (
                False,
                list(Emojis.number_emojis.keys())[
                    list(Emojis.number_emojis.values()).index(react.emoji)
                ],
                False
            )

    def __str__(self) -> str:
        """Return mention of user."""
        return self.user.mention


class AI:
    """The Computer Player for Single-Player games."""

    def __init__(self, symbol: str):
        self.symbol = symbol

    async def get_move(
            self, board: t.Dict[int, str], _: discord.Message
    ) -> t.Tuple[bool, int, bool]:
        """Get move from AI using Minimax strategy."""
        possible_moves = [
            move for move, emoji in board.items()
            if emoji in list(Emojis.number_emojis.values())
        ]

        for symbol in EMOJI_TOKENS:
            for move in possible_moves:
                board_copy = board.copy()
                board_copy[move] = symbol
                if check_win(board_copy):
                    return False, move, False

        open_corners = [i for i in possible_moves if i in (1, 3, 7, 9)]
        if len(open_corners) > 0:
            return False, random.choice(open_corners), False

        if 5 in possible_moves:
            return False, 5, False

        open_edges = [i for i in possible_moves if i in (2, 4, 6, 8)]
        return False, random.choice(open_edges), False

    def __str__(self) -> str:
        """Return `AI` as user name."""
        return "AI"


class Game:
    """Class that contains information and functions about Tic Tac Toe game."""

    def __init__(self, players: t.List[t.Union[Player, AI]], ctx: Context):
        self.players = players
        self.ctx = ctx
        self.channel = ctx.message.channel

        self.board = Emojis.number_emojis.copy()

        self.current = self.players[0]
        self.next = self.players[1]

        self.over = False

    def format_board(self) -> str:
        """Get formatted tic-tac-toe board for message."""
        board = list(self.board.values())
        return "\n".join(
            (
                f"{board[line]} {board[line + 1]} {board[line + 2]}"
                for line in range(0, len(board), 3)
            )
        )

    async def game_over_msg(self, title: str) -> None:
        await self.board_embed.clear_reactions()
        await self.board_embed.edit(embed=discord.Embed(
            title=title,
            description=self.format_board())
        )
        self.over = True
        return

    async def play(self) -> None:
        """Start and handle game."""
        self.board_embed = await self.ctx.send(content="Loading...")

        for x in Emojis.number_emojis.values():
            await self.board_embed.add_reaction(x)
        await self.board_embed.add_reaction(CROSS_EMOJI)

        title = f'{self.current.user.display_name} VS ' \
                f'{self.next if isinstance(self.next, AI) else self.next.user.display_name}'

        await self.board_embed.edit(
            content=None,
            embed=discord.Embed(title=title, description=self.format_board())
        )

        for _ in range(9):
            if isinstance(self.current, Player):
                announcement = await self.ctx.send(
                    f"{self.current.user.mention}, it's your turn! "
                    "React with an emoji to take your go."
                )
            timeout, pos, abandoned = await self.current.get_move(self.board, self.board_embed)

            if isinstance(self.current, Player):
                await announcement.delete()
            if timeout:
                await self.ctx.send(
                    f"{self.current.user.mention} ran out of time. Canceling game."
                )
                self.over = True
                return
            if abandoned:
                await self.game_over_msg(f"{self.current.user.display_name} left the game!")
                return

            self.board[pos] = self.current.symbol
            await self.board_embed.edit(embed=discord.Embed(title=title, description=self.format_board()))
            await self.board_embed.clear_reaction(Emojis.number_emojis[pos])

            if check_win(self.board):
                await self.game_over_msg(
                    f":tada: {self.current if isinstance(self.current, AI) else self.current.user.display_name} "
                    f"won this game! :tada:")
                return

            self.current, self.next = self.next, self.current

        await self.game_over_msg("Its A Draw!")


def is_requester_channel_free() -> t.Callable:
    """Check is channel where command will be invoked free and if the requester is free."""

    async def predicate(ctx: Context) -> bool:
        channel_free = all(
            game.channel != ctx.channel for game in ctx.cog.games if not game.over
        )

        requester_free = all(
            ctx.author not in (player.user for player in game.players if player != "AI")
            for game in ctx.cog.games
            if not game.over
        )
        return channel_free and requester_free

    return check(predicate)


class TicTacToe(Cog):
    """TicTacToe cog contains tic-tac-toe game commands."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.games: t.List[Game] = []
        self.waiting: t.List[discord.Member] = []

    def get_player(
            self,
            ctx: Context,
            announcement: discord.Message,
            reaction: discord.Reaction,
            user: discord.Member,
    ) -> bool:
        """Predicate checking the criteria for the announcement message."""
        if self.already_playing(ctx.author):
            return True

        if (
                user.id not in (ctx.me.id, ctx.author.id)
                and str(reaction.emoji) == HAND_RAISED_EMOJI
                and reaction.message.id == announcement.id
        ):
            if self.already_playing(user):
                self.bot.loop.create_task(
                    ctx.send(f"{user.mention} You're already playing a game!")
                )
                self.bot.loop.create_task(announcement.remove_reaction(reaction, user))
                return False

            if user in self.waiting:
                self.bot.loop.create_task(
                    ctx.send(f"{user.mention} Please cancel your game first before joining another one.")
                )
                self.bot.loop.create_task(announcement.remove_reaction(reaction, user))
                return False

            return True

        if (
                user.id == ctx.author.id
                and str(reaction.emoji) == CROSS_EMOJI
                and reaction.message.id == announcement.id
        ):
            return True

        return False

    def already_playing(self, player: discord.Member) -> bool:
        """Check if someone is already in a game."""
        return any(player in game.players for game in self.games)

    @guild_only()
    @is_requester_channel_free()
    @group(name="tictactoe", aliases=("ttt",), invoke_without_command=True)
    async def tic_tac_toe(self, ctx: Context) -> None:
        """Tic Tac Toe game. Play against friends or AI. Use reactions to add your mark to field."""
        announcement = await ctx.send(
            "**Tic Tac Toe**: A new game is about to start!\n"
            f"Press {HAND_RAISED_EMOJI} to play against {ctx.author.mention}!\n"
            f"(Cancel the game with {CROSS_EMOJI}.)"
        )
        self.waiting.append(ctx.author)
        await announcement.add_reaction(HAND_RAISED_EMOJI)
        await announcement.add_reaction(CROSS_EMOJI)

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add",
                check=partial(self.get_player, ctx, announcement),
                timeout=60.0,
            )
        except asyncio.TimeoutError:
            self.waiting.remove(ctx.author)
            await announcement.delete()
            await ctx.send(
                f"{ctx.author.mention} Seems like there's no one here to play"
                f"Use `{ctx.prefix}{ctx.invoked_with} ai` to play against a computer."
            )
            return

        if str(reaction.emoji) == CROSS_EMOJI:
            self.waiting.remove(ctx.author)
            await announcement.delete()
            await ctx.send(f"{ctx.author.mention} Game cancelled.")
            return

        await announcement.delete()
        self.waiting.remove(ctx.author)

        game = Game(
            [Player(ctx.author, ctx, Emojis.cucumber), Player(user, ctx, Emojis.watermelon)],
            ctx,
        )
        self.games.append(game)
        await game.play()

    @tic_tac_toe.group(aliases=["AI", "CPU", "computer", "cpu", "Computer"])
    async def ai(self, ctx: Context, emoji1: t.Union[discord.Emoji, str]) -> None:
        if isinstance(emoji1, str) and len(emoji1) > 1:
            raise discord.ext.commands.EmojiNotFound(emoji1)
        game = Game(
            [Player(ctx.author, ctx, str(emoji1)), AI(Emojis.watermelon)], ctx
        )
        self.games.append(game)
        await game.play()


def setup(bot: Bot) -> None:
    """Load TicTacToe Cog."""
    bot.add_cog(TicTacToe(bot))
