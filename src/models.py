from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    conversation: str
    sender: str
    timestamp: Optional[datetime]
    text: str
    source_file: str
    attachment: Optional[str] = None