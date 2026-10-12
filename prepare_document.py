
import json
import os

INPUT_PATH = "data/nvd_cves.jsonl"
OUTPUT_PATH = "data/processed/cve_documents.jsonl"


def prepare_document(record):
    """Convert one normalized CVE record into a retrieval document."""

    cve_id = record.get("cve_id")
    description = record.get("description")
    published = record.get("published")

    # Reject records without an identifier or useful description
    if not cve_id:
        raise ValueError("CVE record is missing its identifier")

    if not description or not description.strip():
        raise ValueError(f"{cve_id} has no usable description")

    # Build the text that will eventually be embedded
    text = f"{cve_id}: {description.strip()}"

    return {
        "id": cve_id,
        "text": text,
        "metadata": {
            "published": published,
            "source": "NVD",
        },
    }


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as file:
        records = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    documents = [prepare_document(record) for record in records]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    temp_path = OUTPUT_PATH + ".tmp"

    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            for document in documents:
                file.write(json.dumps(document) + "\n")

        os.replace(temp_path, OUTPUT_PATH)

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    print(f"Input records: {len(records)}")
    print(f"Prepared documents: {len(documents)}")
    print(f"Saved to: {OUTPUT_PATH}")

    if documents:
        print("\nSample prepared document:")
        print(json.dumps(documents[0], indent=4))


if __name__ == "__main__":
    main()
