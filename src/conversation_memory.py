from datetime import timedelta


class ConversationMemory:

    def __init__(self):
        self.last_topics = set()

    def should_continue(
        self,
        current_cluster,
        next_message,
        gap_minutes=45,
    ):

        if len(current_cluster) == 0:
            return True

        previous = current_cluster[-1]

        if (
            previous.timestamp is None
            or next_message.timestamp is None
        ):
            return True

        gap = (
            next_message.timestamp
            - previous.timestamp
        )

        if gap > timedelta(minutes=gap_minutes):
            return False

        previous_text = (
            " ".join(
                m.text.lower()
                for m in current_cluster[-8:]
            )
        )

        next_text = next_message.text.lower()

        previous_words = {
            w
            for w in previous_text.split()
            if len(w) > 3
        }

        next_words = {
            w
            for w in next_text.split()
            if len(w) > 3
        }

        overlap = len(
            previous_words.intersection(next_words)
        )

        if overlap >= 2:
            return True

        return True