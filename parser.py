from pathlib import Path

import pandas as pd

from src.cluster import cluster_messages
from src.database import create_database
from src.extractor import IMessageExtractor


PROJECT_ROOT = Path(__file__).parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def message_rows(messages):
    return [
        {
            "conversation": message.conversation,
            "sender": message.sender,
            "direction": message.direction,
            "timestamp": (
                message.timestamp.isoformat(sep=" ")
                if message.timestamp
                else ""
            ),
            "text": message.text,
            "source_file": message.source_file,
            "guid": message.guid,
            "read_receipt": message.read_receipt,
            "attachment": message.attachment,
        }
        for message in messages
    ]


def cluster_rows(clusters):
    return [
        {
            "cluster_id": cluster.cluster_id,
            "conversation": cluster.conversation,
            "start_time": (
                cluster.start_time.isoformat(sep=" ")
                if cluster.start_time
                else ""
            ),
            "end_time": (
                cluster.end_time.isoformat(sep=" ")
                if cluster.end_time
                else ""
            ),
            "message_count": cluster.message_count,
            "participants": cluster.participants,
            "topics": cluster.topics,
            "transcript": cluster.transcript,
            "source_files": cluster.source_files,
        }
        for cluster in clusters
    ]


def build_review_rows(messages, clusters):
    cluster_lookup = {}

    for cluster in clusters:
        key = (
            cluster.conversation,
            cluster.start_time,
            cluster.end_time,
        )
        cluster_lookup[key] = cluster

    review_rows = []

    for cluster in clusters:
        cluster_messages_list = [
            message
            for message in messages
            if (
                message.conversation == cluster.conversation
                and message.timestamp is not None
                and cluster.start_time is not None
                and cluster.end_time is not None
                and cluster.start_time
                <= message.timestamp
                <= cluster.end_time
            )
        ]

        for message in cluster_messages_list:
            review_rows.append(
                {
                    "cluster_id": cluster.cluster_id,
                    "date": (
                        message.timestamp.strftime("%m/%d/%Y")
                        if message.timestamp
                        else ""
                    ),
                    "time": (
                        message.timestamp.strftime("%I:%M:%S %p")
                        if message.timestamp
                        else ""
                    ),
                    "sender": message.sender,
                    "direction": message.direction,
                    "message": message.text,
                    "topics": cluster.topics,
                    "conversation": message.conversation,
                    "source_file": message.source_file,
                    "guid": message.guid,
                    "attachment": message.attachment,
                }
            )

    return review_rows


def main():
    extractor = IMessageExtractor(INPUT_DIR)
    messages = extractor.extract_all()

    messages_df = pd.DataFrame(message_rows(messages))

    if not messages_df.empty:
        messages_df = messages_df.sort_values(
            by=["timestamp", "source_file"],
            na_position="last",
        )

    messages_file = OUTPUT_DIR / "messages.csv"

    messages_df.to_csv(
        messages_file,
        index=False,
        encoding="utf-8-sig",
    )

    clusters = cluster_messages(
        messages,
        maximum_gap_minutes=45,
        minimum_topic_split_messages=3,
    )

    clusters_df = pd.DataFrame(cluster_rows(clusters))

    cluster_index_file = (
        OUTPUT_DIR / "conversation_clusters_index.csv"
    )

    cluster_full_file = (
        OUTPUT_DIR / "conversation_clusters_full.csv"
    )

    index_columns = [
        "cluster_id",
        "conversation",
        "start_time",
        "end_time",
        "message_count",
        "participants",
        "topics",
        "source_files",
    ]

    clusters_df[index_columns].to_csv(
        cluster_index_file,
        index=False,
        encoding="utf-8-sig",
    )

    clusters_df.to_csv(
        cluster_full_file,
        index=False,
        encoding="utf-8-sig",
    )

    review_df = pd.DataFrame(
        build_review_rows(messages, clusters)
    )

    review_file = OUTPUT_DIR / "conversation_review.csv"

    review_df.to_csv(
        review_file,
        index=False,
        encoding="utf-8-sig",
    )

    database_file = OUTPUT_DIR / "bridget_messages.db"

    create_database(
        database_file,
        messages,
        clusters,
    )

    print(f"\nTotal messages extracted: {len(messages_df):,}")
    print(f"Conversation clusters created: {len(clusters_df):,}")
    print(f"Review rows created: {len(review_df):,}")
    print(f"Saved messages: {messages_file}")
    print(f"Saved cluster index: {cluster_index_file}")
    print(f"Saved full clusters: {cluster_full_file}")
    print(f"Saved review file: {review_file}")
    print(f"Saved database: {database_file}")


if __name__ == "__main__":
    main()