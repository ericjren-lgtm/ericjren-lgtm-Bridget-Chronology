from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from src.models import Message
from src.utils import clean_text


class IMessageExtractor:

    def __init__(self, input_folder):
        self.input_folder = Path(input_folder)

    def extract_all(self):

        messages = []

        html_files = sorted(self.input_folder.glob("*.html"))

        print(f"Found {len(html_files)} html files")

        for html_file in html_files:

            print(f"Reading {html_file.name}")

            msgs = self.extract_file(html_file)

            messages.extend(msgs)

        return messages

    def extract_file(self, file_path):

        with open(file_path, "r", encoding="utf-8") as f:

            soup = BeautifulSoup(f.read(), "lxml")

        messages = []

        for div in soup.select("div.message"):

            direction = "Unknown"

            sender = ""

            timestamp = None
            text = ""

            sent = div.select_one("div.sent")
            received = div.select_one("div.received")

            block = sent if sent else received

            if sent:
                direction = "Sent"

            if received:
                direction = "Received"

            if block is None:
                continue

            sender_tag = block.select_one("span.sender")

            if sender_tag:
                sender = clean_text(sender_tag.get_text())

            ts = block.select_one("span.timestamp")

            if ts:

                try:

                    timestamp = datetime.fromisoformat(
                        clean_text(ts.get_text())
                    )

                except:

                    timestamp = None

            bubble = block.select_one("span.bubble")

            if bubble:
                text = clean_text(bubble.get_text())

            messages.append(

                Message(
                    conversation=file_path.stem,
                    sender=sender,
                    timestamp=timestamp,
                    text=text,
                    source_file=file_path.name,
                    attachment=None,
                )

            )

        return messages