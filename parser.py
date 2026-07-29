from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
import re
import html
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

BRIDGET_NUMBER = "5184695163"

messages = []
def clean_text(text):
    if text is None:
        return ""

    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_phone(phone):
    if phone is None:
        return ""

    digits = re.sub(r"\D", "", phone)

    if digits.startswith("1"):
        digits = digits[1:]

    return digits
def get_html_files():
    files = sorted(INPUT_DIR.glob("*.html"))

    print(f"\nFound {len(files)} HTML files.\n")

    for f in files:
        print(" •", f.name)

    return files
def load_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return BeautifulSoup(f.read(), "lxml")


def main():

    html_files = get_html_files()

    if len(html_files) == 0:
        print("No HTML files found in input folder.")
        return

    for file in html_files:
        print(f"\nLoading {file.name}...")

        soup = load_html(file)

        print("   ✓ Loaded successfully")

    print("\nAll files loaded.")


if __name__ == "__main__":
    main()