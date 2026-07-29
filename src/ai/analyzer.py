from dataclasses import dataclass
from typing import List


@dataclass
class AnalysisResult:

    summary: str

    topics: List[str]

    entities: List[str]

    facts: List[str]

    commitments: List[str]

    importance_score: float


class ConversationAnalyzer:

    def analyze(self, conversation):

        return AnalysisResult(

            summary="",

            topics=[],

            entities=[],

            facts=[],

            commitments=[],

            importance_score=0.0,

        )