import re


def gurkan_check(target: str) -> bool:
    """Returns a bool stating if the name given is a gurkan or not."""
    return bool(re.search(r"gurk|urkan", target.lower()))


def gurkan_rate(name: str) -> float:
    """Returns the rate of gurkan in the name given."""
    if name == "":
        return 0.0
    gurkanness = 0
    for match in re.finditer("gurkan|urkan|gurk", name.lower()):
        begin, end = match.span()
        gurkanness += end - begin
    return int((gurkanness / len(name)) * 100)
