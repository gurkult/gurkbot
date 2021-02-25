from discord.ext import commands


class Command(commands.Command):
    """
    A `discord.ext.commands.Command` subclass which supports root aliases.

    A `root_aliases` keyword argument is added, which is a sequence of alias names that will act as
    top-level commands rather than being aliases of the command's group.

    Example:
        `!gh issue 72` can also be called as `!issue 72`.
        `!gh src eval` can also be called as `!src eval`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_aliases = kwargs.get("root_aliases", [])

        if not isinstance(self.root_aliases, (list, tuple)):
            raise TypeError(
                "Root aliases must bbe of type list or tuple, containing strings."
            )
