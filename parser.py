from pathlib import Path
import pandas as pd

from src.extractor import IMessageExtractor

PROJECT_ROOT = Path(__file__).parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def main():

    extractor = IMessageExtractor(INPUT_DIR)

    messages = extractor.extract_all()

    print(f"\nTotal messages extracted: {len(messages)}")

    rows = []

    for m in messages:

        rows.append(
            {
                "conversation": m.conversation,
                "sender": m.sender,
                "timestamp": m.timestamp,
                "text": m.text,
                "source_file": m.source_file,
                "attachment": m.attachment,
            }
        )

    df = pd.DataFrame(rows)

    outfile = OUTPUT_DIR / "messages.csv"

    df.to_csv(outfile, index=False)

    print(f"\nSaved {outfile}")


if __name__ == "__main__":
    main()