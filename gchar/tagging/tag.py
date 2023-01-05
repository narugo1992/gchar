import re

RE_TAG_SPECIAL = re.compile(r'([\\()])')


def tag_escape(tag: str) -> str:
    return RE_TAG_SPECIAL.sub(r'\\\1', tag)
