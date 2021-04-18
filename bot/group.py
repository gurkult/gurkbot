from discord.ext import commands


class Group(commands.Group):
    """
    A `discord.ext.commands.Group` subclass which supports root aliases.

    A `root_aliases` keyword argument is added, which is a sequence of alias names that will act as
    top-level groups rather than being aliases of the group's group

    Example:
        `!cmd gh issue 72` can also be called as `!gh issue 72`.
        `!cmd src eval` can also be called as `!gh src eval`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_aliases = kwargs.get("root_aliases", [])

        if not isinstance(self.root_aliases, (list, tuple)):
            raise TypeError(
                "Root aliases must be of type list or tuple, containing strings."
            )
