from dataclasses import dataclass


@dataclass
class AIResult:

    summary: str

    primary_topics: list

    secondary_topics: list

    people: list

    organizations: list

    locations: list

    financial_items: list

    commitments: list

    questions: list

    sentiment: dict