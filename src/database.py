import sqlite3
from pathlib import Path
from typing import Iterable

from src.models import Message
from src.cluster import ConversationCluster


MESSAGE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guid TEXT,
    conversation TEXT NOT NULL,
    sender TEXT NOT NULL,
    direction TEXT NOT NULL,
    timestamp TEXT,
    text TEXT,
    source_file TEXT NOT NULL,
    read_receipt TEXT,
    attachment TEXT
);
"""

CLUSTER_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS conversation_clusters (
    cluster_id TEXT PRIMARY KEY,
    conversation TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT,
    message_count INTEGER NOT NULL,
    participants TEXT,
    topics TEXT,
    transcript TEXT,
    source_files TEXT
);
"""

INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_messages_timestamp
ON messages(timestamp);

CREATE INDEX IF NOT EXISTS idx_messages_sender
ON messages(sender);

CREATE INDEX IF NOT EXISTS idx_messages_conversation
ON messages(conversation);

CREATE INDEX IF NOT EXISTS idx_messages_guid
ON messages(guid);

CREATE INDEX IF NOT EXISTS idx_clusters_start_time
ON conversation_clusters(start_time);

CREATE INDEX IF NOT EXISTS idx_clusters_topics
ON conversation_clusters(topics);
"""


def create_database(
    database_path: Path,
    messages: Iterable[Message],
    clusters: Iterable[ConversationCluster],
) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)

    if database_path.exists():
        database_path.unlink()

    connection = sqlite3.connect(database_path)

    try:
        connection.execute(MESSAGE_TABLE_SQL)
        connection.execute(CLUSTER_TABLE_SQL)
        connection.executescript(INDEX_SQL)

        message_rows = [
            (
                message.guid,
                message.conversation,
                message.sender,
                message.direction,
                (
                    message.timestamp.isoformat(sep=" ")
                    if message.timestamp
                    else None
                ),
                message.text,
                message.source_file,
                message.read_receipt,
                message.attachment,
            )
            for message in messages
        ]

        connection.executemany(
            """
            INSERT INTO messages (
                guid,
                conversation,
                sender,
                direction,
                timestamp,
                text,
                source_file,
                read_receipt,
                attachment
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            message_rows,
        )

        cluster_rows = [
            (
                cluster.cluster_id,
                cluster.conversation,
                (
                    cluster.start_time.isoformat(sep=" ")
                    if cluster.start_time
                    else None
                ),
                (
                    cluster.end_time.isoformat(sep=" ")
                    if cluster.end_time
                    else None
                ),
                cluster.message_count,
                cluster.participants,
                cluster.topics,
                cluster.transcript,
                cluster.source_files,
            )
            for cluster in clusters
        ]

        connection.executemany(
            """
            INSERT INTO conversation_clusters (
                cluster_id,
                conversation,
                start_time,
                end_time,
                message_count,
                participants,
                topics,
                transcript,
                source_files
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            cluster_rows,
        )

        connection.commit()

    finally:
        connection.close()