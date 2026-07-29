import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup

from src.models import Message
from src.utils import clean_text, normalize_sender


TIMESTAMP_FORMAT = "%b %d, %Y %I:%M:%S %p"


class IMessageExtractor:
    def __init__(self, input_folder: Path):
        self.input_folder = Path(input_folder)

    def extract_all(self) -> List[Message]:
        messages: List[Message] = []
        html_files = sorted(self.input_folder.glob("*.html"))

        print(f"Found {len(html_files)} HTML files.")

        for html_file in html_files:
            print(f"Reading {html_file.name}")
            messages.extend(self.extract_file(html_file))

        return messages

    def extract_file(self, file_path: Path) -> List[Message]:
        with file_path.open(
            "r",
            encoding="utf-8",
            errors="replace",
        ) as file_handle:
            soup = BeautifulSoup(file_handle, "lxml")

        messages: List[Message] = []

        for message_div in soup.select("div.message"):
            sent_block = message_div.select_one("div.sent")
            received_block = message_div.select_one("div.received")

            block = sent_block or received_block

            if block is None:
                continue

            direction = "Sent" if sent_block is not None else "Received"

            sender_tag = block.select_one("span.sender")

            raw_sender = (
                clean_text(sender_tag.get_text(" ", strip=True))
                if sender_tag
                else ""
            )

            sender = normalize_sender(raw_sender)

            timestamp, guid, read_receipt = self._extract_timestamp_data(
                block
            )

            text = self._extract_message_text(block)
            attachment = self._extract_attachment(block)

            messages.append(
                Message(
                    conversation=file_path.stem,
                    sender=sender,
                    direction=direction,
                    timestamp=timestamp,
                    text=text,
                    source_file=file_path.name,
                    guid=guid,
                    read_receipt=read_receipt,
                    attachment=attachment,
                )
            )

        return messages

    @staticmethod
    def _extract_message_text(block) -> str:
        text_parts: List[str] = []

        for bubble_tag in block.select("span.bubble"):
            text = clean_text(
                bubble_tag.get_text(" ", strip=True)
            )

            if text:
                text_parts.append(text)

        return "\n".join(text_parts)

    @staticmethod
    def _extract_timestamp_data(
        block,
    ) -> Tuple[Optional[datetime], Optional[str], Optional[str]]:
        timestamp_tag = block.select_one("span.timestamp")

        if timestamp_tag is None:
            return None, None, None

        anchor = timestamp_tag.select_one("a")

        timestamp: Optional[datetime] = None
        guid: Optional[str] = None
        read_receipt: Optional[str] = None

        if anchor is not None:
            timestamp_text = clean_text(
                anchor.get_text(" ", strip=True)
            )

            try:
                timestamp = datetime.strptime(
                    timestamp_text,
                    TIMESTAMP_FORMAT,
                )
            except ValueError:
                timestamp = None

            href = anchor.get("href", "")

            guid_match = re.search(
                r"message-guid=([^&]+)",
                href,
            )

            if guid_match:
                guid = guid_match.group(1)

        full_timestamp_text = clean_text(
            timestamp_tag.get_text(" ", strip=True)
        )

        anchor_text = (
            clean_text(anchor.get_text(" ", strip=True))
            if anchor is not None
            else ""
        )

        if anchor_text:
            read_receipt = full_timestamp_text.replace(
                anchor_text,
                "",
                1,
            ).strip()
        else:
            read_receipt = full_timestamp_text.strip()

        if not read_receipt:
            read_receipt = None

        return timestamp, guid, read_receipt

    @staticmethod
    def _extract_attachment(block) -> Optional[str]:
        attachment_paths: List[str] = []

        for tag in block.select("img, video, audio, source"):
            source_path = tag.get("src")

            if source_path:
                attachment_paths.append(source_path)

        for tag in block.select("a"):
            href = tag.get("href", "")

            if href and not href.startswith("sms://"):
                attachment_paths.append(href)

        unique_paths = list(dict.fromkeys(attachment_paths))

        if not unique_paths:
            return None

        return " | ".join(unique_paths)