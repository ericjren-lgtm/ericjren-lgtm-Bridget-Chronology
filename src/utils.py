import html
import re
from typing import Optional


BRIDGET_ALIASES = {
    "best mom ever",
    "bridget",
    "bridget ren",
    "bridget keaney",
    "bridget ren-keuney",
    "bridget ren-keeney",
}

ERIC_ALIASES = {
    "me",
    "eric",
    "eric ren",
}


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_sender(sender: Optional[str]) -> str:
    if not sender:
        return "Unknown"

    cleaned = clean_text(sender)
    key = cleaned.casefold()

    if key in ERIC_ALIASES:
        return "Eric"

    if key in BRIDGET_ALIASES:
        return "Bridget"

    return cleaned