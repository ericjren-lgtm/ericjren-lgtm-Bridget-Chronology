from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Sequence, Set

from src.models import Message


@dataclass
class ConversationCluster:
    cluster_id: str
    conversation: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    message_count: int
    participants: str
    topics: str
    transcript: str
    source_files: str


TOPIC_PATTERNS: Dict[str, Sequence[str]] = {
    "Financial Partnership / Rockefeller": (
        r"\brockefeller\b",
        r"\bfidelity\b",
        r"\bbill pay\b",
        r"\bdirect deposit\b",
        r"\bjoint account\b",
        r"\bbank account\b",
        r"\bbudget\b",
        r"\bwire\b",
        r"\btransfer\b",
        r"\bmonthly funding\b",
        r"\bcash flow\b",
        r"\bfinancial\b",
        r"\bmoney\b",
        r"\bexpenses?\b",
        r"\btaxes?\b",
    ),
    "Parenting": (
        r"\bcolin\b",
        r"\bcaroline\b",
        r"\bschool\b",
        r"\bcba\b",
        r"\browing\b",
        r"\bpractice\b",
        r"\bpick(?:ing)? up\b",
        r"\bdrop(?:ping)? off\b",
        r"\bdoctor\b",
        r"\bappointment\b",
        r"\bhomework\b",
        r"\bcollege\b",
        r"\bparent\b",
        r"\bkids?\b",
    ),
    "NY Properties": (
        r"\bcrescent\b",
        r"\bfitch\b",
        r"\bsaratoga\b",
        r"\bnew york\b",
        r"\bny property\b",
        r"\bhouse\b",
        r"\bhome\b",
        r"\bmortgage\b",
        r"\bcontractor\b",
        r"\brenovation\b",
    ),
    "FL Properties": (
        r"\bmarathon\b",
        r"\bkey west\b",
        r"\bflorida\b",
        r"\bkeys\b",
        r"\bcondo\b",
        r"\bhoa\b",
    ),
    "Farm Operations": (
        r"\bfarm\b",
        r"\bbarn\b",
        r"\barena\b",
        r"\bhorse\b",
        r"\bhorses\b",
        r"\bgoat\b",
        r"\bhay\b",
        r"\bfence\b",
        r"\bpaddock\b",
        r"\btractor\b",
        r"\bkubota\b",
        r"\bbobcat\b",
        r"\bmanure\b",
        r"\bstall\b",
        r"\bpasture\b",
        r"\bfeed\b",
    ),
    "Career Transition": (
        r"\bmainline\b",
        r"\bwork\b",
        r"\bjob\b",
        r"\bcareer\b",
        r"\bretire\b",
        r"\bresign\b",
        r"\bleav(?:e|ing) work\b",
        r"\bconsulting\b",
        r"\bmis security\b",
        r"\bvectis\b",
        r"\bbusiness\b",
        r"\bincome\b",
        r"\bsalary\b",
    ),
    "Marriage / Separation": (
        r"\bmarriage\b",
        r"\brelationship\b",
        r"\bcounsel(?:ing|or)\b",
        r"\btherapy\b",
        r"\bseparat(?:e|ion)\b",
        r"\bdivorce\b",
        r"\bbasement\b",
        r"\breconcil(?:e|iation)\b",
        r"\blove\b",
        r"\btrust\b",
        r"\bairport\b",
        r"\bboundar(?:y|ies)\b",
    ),
}


COMPILED_TOPIC_PATTERNS: Dict[str, List[re.Pattern[str]]] = {
    topic: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for topic, patterns in TOPIC_PATTERNS.items()
}


def detect_topics(text: str) -> Set[str]:
    detected: Set[str] = set()

    for topic, patterns in COMPILED_TOPIC_PATTERNS.items():
        if any(pattern.search(text) for pattern in patterns):
            detected.add(topic)

    return detected


def should_split_for_topic_shift(
    current_messages: List[Message],
    next_message: Message,
) -> bool:
    if not current_messages:
        return False

    current_text = " ".join(message.text for message in current_messages[-8:])
    current_topics = detect_topics(current_text)
    next_topics = detect_topics(next_message.text)

    if not current_topics or not next_topics:
        return False

    return current_topics.isdisjoint(next_topics)


def format_transcript(messages: List[Message]) -> str:
    lines: List[str] = []

    for message in messages:
        timestamp = (
            message.timestamp.strftime("%Y-%m-%d %I:%M:%S %p")
            if message.timestamp
            else "Unknown time"
        )

        text = message.text.strip()

        if not text and message.attachment:
            text = f"[Attachment: {message.attachment}]"
        elif message.attachment:
            text = f"{text}\n[Attachment: {message.attachment}]"

        lines.append(f"{timestamp} | {message.sender}: {text}")

    return "\n".join(lines)


def build_cluster(
    cluster_number: int,
    messages: List[Message],
) -> ConversationCluster:
    start_time = messages[0].timestamp if messages else None
    end_time = messages[-1].timestamp if messages else None

    combined_text = " ".join(message.text for message in messages)
    topics = sorted(detect_topics(combined_text))

    participants = sorted(
        {
            message.sender
            for message in messages
            if message.sender and message.sender != "Unknown"
        }
    )

    source_files = sorted({message.source_file for message in messages})

    return ConversationCluster(
        cluster_id=f"B-{cluster_number:05d}",
        conversation=messages[0].conversation,
        start_time=start_time,
        end_time=end_time,
        message_count=len(messages),
        participants=" | ".join(participants),
        topics=" | ".join(topics),
        transcript=format_transcript(messages),
        source_files=" | ".join(source_files),
    )


def cluster_messages(
    messages: List[Message],
    maximum_gap_minutes: int = 45,
    minimum_topic_split_messages: int = 3,
) -> List[ConversationCluster]:
    valid_messages = sorted(
        messages,
        key=lambda message: (
            message.conversation,
            message.timestamp or datetime.max,
        ),
    )

    clusters: List[ConversationCluster] = []
    current_messages: List[Message] = []
    current_conversation: Optional[str] = None
    cluster_number = 1

    for message in valid_messages:
        if not current_messages:
            current_messages = [message]
            current_conversation = message.conversation
            continue

        previous_message = current_messages[-1]

        conversation_changed = message.conversation != current_conversation

        time_gap_exceeded = False

        if previous_message.timestamp and message.timestamp:
            time_gap = message.timestamp - previous_message.timestamp
            time_gap_exceeded = time_gap > timedelta(
                minutes=maximum_gap_minutes
            )

        topic_shift = (
            len(current_messages) >= minimum_topic_split_messages
            and should_split_for_topic_shift(current_messages, message)
        )

        if conversation_changed or time_gap_exceeded or topic_shift:
            clusters.append(
                build_cluster(cluster_number, current_messages)
            )
            cluster_number += 1
            current_messages = [message]
            current_conversation = message.conversation
        else:
            current_messages.append(message)

    if current_messages:
        clusters.append(build_cluster(cluster_number, current_messages))

    return clusters