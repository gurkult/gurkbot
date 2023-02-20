import os
from typing import Generator

from bot import constants

EXTENSIONS: list[str] = []  # All extensions.


def unqualify(name: str) -> str:
    """Return an unqualified name given a qualified module/package `name`."""
    return name.rsplit(".", maxsplit=1)[-1]


def walk_extensions() -> Generator[str, None, None]:
    """Yield extensions from the configured constants.EXTENSIONS subpackage."""
    for extension in constants.EXTENSIONS.glob("*/*.py"):
        if extension.name.startswith("_"):
            continue  # ignore files starting with _
        dot_path = str(extension).replace(os.sep, ".")[:-3]  # remove the .py
        yield dot_path
