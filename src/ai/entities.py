from dataclasses import dataclass


@dataclass
class Entity:

    entity_type: str

    entity_name: str

    confidence: float