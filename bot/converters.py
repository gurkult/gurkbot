from discord.ext.commands import BadArgument, Context, Converter


class OffTopicName(Converter):
    """
    A converter that ensures an added off-topic name is valid.

    Adopted from python-discord/bot https://github.com/python-discord/bot/blob/master/bot/converters.py#L344
    """

    allowed_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ!?'`-"
    table = str.maketrans(allowed_characters, "𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹ǃ？’’-")

    async def convert(self, ctx: Context, argument: str) -> str:
        """Attempt to replace any invalid characters with their approximate Unicode equivalent."""
        argument = argument.lower()

        # Chain multiple words to a single one
        argument = "-".join(argument.split())

        if not (2 <= len(argument) <= 29):
            raise BadArgument("Channel name must be between 2 and 96 chars long")

        elif not all(c.isalnum() or c in self.allowed_characters for c in argument):
            raise BadArgument(
                "Channel name must only consist of "
                "alphanumeric characters, minus signs or apostrophes."
            )

        # Replace invalid characters with unicode alternatives.

        return argument.translate(self.table)
