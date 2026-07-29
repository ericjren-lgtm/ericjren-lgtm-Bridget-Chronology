from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    conversation: str
    sender: str
    direction: str
    timestamp: Optional[datetime]
    text: str
    source_file: str
    guid: Optional[str] = None
    read_receipt: Optional[str] = None
    attachment: Optional[str] = None