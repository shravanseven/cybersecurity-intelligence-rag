
import json


RAW_PATH = "data/kev_vulnerabilities.jsonl"
DOCUMENTS_PATH = "data/processed/kev_documents.jsonl"


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def main():
    raw_records = load_jsonl(RAW_PATH)
    documents = load_jsonl(DOCUMENTS_PATH)

    raw_cve_ids = [record.get("cveID") for record in raw_records]
    document_ids = [document.get("id") for document in documents]
    normalized_cve_ids = [
        document.get("metadata", {}).get("cve_id")
        for document in documents
    ]

    errors = []

    # 1. Check record counts
    if len(raw_records) != len(documents):
        errors.append("Raw and prepared record counts do not match.")

    # 2. Check uniqueness
    if len(document_ids) != len(set(document_ids)):
        errors.append("Duplicate document IDs found.")

    if len(normalized_cve_ids) != len(set(normalized_cve_ids)):
        errors.append("Duplicate CVE IDs found in prepared documents.")

    # 3. Validate each prepared document
    for index, document in enumerate(documents, start=1):
        doc_id = document.get("id")
        text = document.get("text")
        metadata = document.get("metadata")

        if not isinstance(doc_id, str) or not doc_id.startswith("CISA_KEV:"):
            errors.append(f"Record {index}: invalid source-qualified ID.")

        if not isinstance(text, str) or not text.strip():
            errors.append(f"Record {index}: missing or empty text.")

        if not isinstance(metadata, dict):
            errors.append(f"Record {index}: metadata must be a dictionary.")
            continue

        if metadata.get("source") != "CISA_KEV":
            errors.append(f"Record {index}: incorrect source metadata.")

        if not metadata.get("cve_id"):
            errors.append(f"Record {index}: missing CVE ID in metadata.")

        if doc_id != f"CISA_KEV:{metadata.get('cve_id')}":
            errors.append(f"Record {index}: ID and metadata CVE ID do not match.")

    # 4. Confirm every raw CVE appears in the prepared output
    if set(raw_cve_ids) != set(normalized_cve_ids):
        errors.append("Raw and prepared CVE ID sets do not match.")

    # 5. Report results
    print("Raw records:", len(raw_records))
    print("Prepared documents:", len(documents))
    print("Unique document IDs:", len(set(document_ids)))
    print("Unique CVE IDs:", len(set(normalized_cve_ids)))

    if errors:
        print("\nValidation FAILED.")
        for error in errors:
            print("-", error)
        raise SystemExit(1)

    print("\nValidation PASSED.")
    print("All prepared documents passed the checks.")


if __name__ == "__main__":
    main()
