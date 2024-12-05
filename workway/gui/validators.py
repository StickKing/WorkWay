"""Module contains validators."""
import re


def is_number(value: str | None) -> bool:
    """Is value if number."""
    if value is None:
        return False
    temp = r"[0-9]+\.[0-9]+"
    return value.isdigit() or bool(re.match(temp, value))
