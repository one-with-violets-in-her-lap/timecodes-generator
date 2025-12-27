import re
from typing import Literal


def join_and_compile_regex_patterns(
    patterns: list[str], flags: re.RegexFlag | Literal[0] = 0
):
    """Combines regex patterns by chaining them with OR (`|`) operator

    Examples
    --------
    >>> join_and_compile_regex_patterns(["foo", "bar"])
    Pattern("foo|bar")

    :param flags: Regex flags. Can be combined using bitwise OR operator: `re.IGNORECASE | re.MULTILINE`

    :return: Compiled regex
    """
    return re.compile("|".join(patterns), flags=flags)
