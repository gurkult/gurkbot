import re


def gurkan_check(target: str) -> bool:
    """Returns a bool stating if the name given is a gurkan or not."""
    return bool(re.search(r"gurk|urkan", target.lower()))


def gurkan_rate(name: str) -> int:
    """Returns the rate of gurkan in the name given."""
    search = re.search(r"gurk|urkan", name.lower())
    span = search.span() if search else (0, 0)
    return int((span[1] - span[0]) / len(name) * 100)
