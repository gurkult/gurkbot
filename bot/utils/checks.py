from typing import Optional

from disnake.ext.commands import CheckFailure


class InWhitelistCheckFailure(CheckFailure):
    """Raised when the `in_whitelist` check fails."""

    def __init__(self, redirect_channel: Optional[int]) -> None:
        self.redirect_channel = redirect_channel

        if redirect_channel is not None:
            redirect_message = (
                f"Here. Please use the <#{redirect_channel}> channel instead"
            )
        else:
            redirect_message = ""

        error_message = f"You are not allowed to use that command{redirect_message}."

        super().__init__(error_message)
