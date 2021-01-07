import re

from fuzzywuzzy import process


def gurkan_check(target: str) -> bool:
    """Returns a bool stating if the name given is a gurkan or not."""
    return bool(re.search(r"gurk|urkan", target.lower()))


def gurkan_rate(name: str) -> int:
    """Returns the rate of gurkan in the name given."""
    return process.extractOne("gurkan", [name.lower()])[1]
