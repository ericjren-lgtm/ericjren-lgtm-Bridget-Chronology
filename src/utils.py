import html
import re


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()