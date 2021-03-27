from discord.ext.commands import BadArgument, Context, Converter


class OffTopicName(Converter):
    """
    A converter that ensures an added off-topic name is valid.

    Taken from python-discord/bot https://github.com/python-discord/bot/blob/master/bot/converters.py#L344
    """

    async def convert(self, ctx: Context, argument: str) -> str:
        """Attempt to replace any invalid characters with their approximate Unicode equivalent."""
        allowed_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ!?'`-"

        # Chain multiple words to a single one
        argument = "-".join(argument.split())

        if not (2 <= len(argument) <= 96):
            raise BadArgument("Channel name must be between 2 and 96 chars long")

        elif not all(c.isalnum() or c in allowed_characters for c in argument):
            raise BadArgument(
                "Channel name must only consist of "
                "alphanumeric characters, minus signs or apostrophes."
            )

        # Replace invalid characters with unicode alternatives.
        table = str.maketrans(allowed_characters, "𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹ǃ？’’-")
        return argument.translate(table)
