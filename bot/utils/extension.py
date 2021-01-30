import glob
import importlib
import inspect
import typing as t


def dotted_path() -> t.Generator:
    """Prepares all the files that are in bot/exts."""
    files = [
        file
        for file in glob.glob("bot/exts/*/*.py", recursive=True)
        if "__" not in file
    ]  # ignoring files which have double underscores

    for value in files:
        yield "{}".format(value.replace("/", ".")[:-3])  # removing the py


def qualify_extension() -> t.Union[set, bool]:
    """Returns only the set of modules that actually have cogs."""
    extensions = set()
    for module in dotted_path():
        imported = importlib.import_module(module)
        try:
            if inspect.isfunction(getattr(imported, "setup")):
                extensions.add(module)
        except AttributeError:
            continue
    return extensions


EXTENSIONS = qualify_extension()
