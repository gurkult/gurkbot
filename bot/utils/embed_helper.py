from random import choice
from typing import Optional, Tuple, Union

from discord import Embed

from ..constants import Colours, ERROR_REPLIES, NEGATIVE_REPLIES, POSITIVE_REPLIES


class EmbedHelper:
    """doctstring."""

    @staticmethod
    def embed_helper(
        title: str,
        description: str,
        colour: int,
        url: Optional[str] = None,
    ) -> Embed:
        """Method that creates an embed."""
        embed = Embed(title=title, description=description, colour=colour, url=url)

        return embed

    @classmethod
    def information(
        cls,
        *,
        title: Optional[str] = None,
        description: str,
        url: Optional[str] = None,
        **fields: Union[str, Tuple[str, bool]]
    ) -> Embed:
        """Embed used in a positive context."""
        title_ = title or choice(POSITIVE_REPLIES)

        return cls.embed_helper(
            title=title_,
            description=description,
            url=url,
            colour=Colours.green,
        )

    @classmethod
    def error(
        cls,
        *,
        title: Optional[str] = None,
        description: str,
        url: Optional[str] = None,
        **fields: Union[str, Tuple[str, bool]]
    ) -> Embed:
        """Embed used for displaying errors."""
        title_ = title or choice(ERROR_REPLIES)

        return cls.embed_helper(
            title=title_,
            description=description,
            url=url,
            colour=Colours.soft_red,
        )

    @classmethod
    def warning(
        cls,
        *,
        title: Optional[str] = None,
        description: str,
        url: Optional[str] = None,
        **fields: Union[str, Tuple[str, bool]]
    ) -> Embed:
        """Embed used to blah."""
        title_ = title or choice(NEGATIVE_REPLIES)

        return cls.embed_helper(
            title=title_,
            description=description,
            url=url,
            colour=Colours.yellow,
        )
