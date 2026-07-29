from dataclasses import dataclass


@dataclass
class Commitment:

    speaker: str

    text: str

    completed: bool

    confidence: float