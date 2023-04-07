# Source: https://github.com/onerandomusername/monty-python/blob/817344b4dbee5b30be4d915460965efb3509b3bf/monty/exts/utils/delete.py  # noqa: E501


import disnake
from disnake.ext import commands
from loguru import logger

from bot.bot import Bot
from bot.utils.messages import DELETE_ID_V1


class DeleteManager(commands.Cog):
    """Handle delete buttons being pressed."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    # button schema
    # prefix:PERMS:USERID
    # optional :MSGID
    @commands.Cog.listener("on_button_click")
    async def handle_v2_button(self, inter: disnake.MessageInteraction) -> None:
        """Delete a message if the user is authorized to delete the message."""
        if not inter.component.custom_id.startswith(DELETE_ID_V1):
            return

        custom_id = inter.component.custom_id.removeprefix(DELETE_ID_V1)

        perms, user_id, *extra = custom_id.split(":")
        delete_msg = None
        if extra:
            if extra[0]:
                delete_msg = int(extra[0])

        perms, user_id = int(perms), int(user_id)

        # check if the user id is the allowed user OR check if the user has any of the permissions allowed
        if not (is_orig_author := inter.author.id == user_id):
            permissions = disnake.Permissions(perms)
            user_permissions = inter.permissions
            if not permissions.value & user_permissions.value:
                await inter.response.send_message(
                    "Sorry, this delete button is not for you!", ephemeral=True
                )
                return

        if (
            not hasattr(inter.channel, "guild")
            or not (myperms := inter.channel.permissions_for(inter.me)).read_messages
        ):
            await inter.response.defer()
            await inter.delete_original_message()
            return

        await inter.message.delete()
        if not delete_msg or not myperms.manage_messages or not is_orig_author:
            return
        if msg := inter.bot.get_message(delete_msg):
            if msg.edited_at:
                return
        else:
            msg = inter.channel.get_partial_message(delete_msg)
        try:
            await msg.delete()
        except disnake.NotFound:
            pass
        except disnake.Forbidden:
            logger.warning("Cache is unreliable, or something weird occured.")


def setup(bot: Bot) -> None:
    """Add the DeleteManager to the bot."""
    bot.add_cog(DeleteManager(bot))
