
import json

FILE_PATH = "data/processed/cve_documents.jsonl"

documents = []

with open(FILE_PATH, "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        if not line.strip():
            continue

        try:
            document = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON on line {line_number}"
            ) from error

        # Validate the document structure
        for field in ("id", "text", "metadata"):
            if field not in document:
                raise ValueError(
                    f"Missing '{field}' on line {line_number}"
                )

        if not isinstance(document["metadata"], dict):
            raise ValueError(
                f"Metadata must be a dictionary on line {line_number}"
            )

        if not document["id"]:
            raise ValueError(f"Empty ID on line {line_number}")

        if not isinstance(document["text"], str) or not document["text"].strip():
            raise ValueError(f"Empty text on line {line_number}")

        if "published" not in document["metadata"]:
            raise ValueError(
                f"Missing publication metadata on line {line_number}"
            )

        if document["metadata"].get("source") != "NVD":
            raise ValueError(
                f"Unexpected source on line {line_number}"
            )

        documents.append(document)

ids = [document["id"] for document in documents]

if len(ids) != len(set(ids)):
    raise ValueError("Duplicate document IDs found")

print("Total documents:", len(documents))
print("Unique document IDs:", len(set(ids)))
print("All documents have valid structure and non-empty text.")
