
import json
import os


INPUT_PATH = "data/kev_vulnerabilities.jsonl"
OUTPUT_PATH = "data/processed/kev_documents.jsonl"


def prepare_document(record):
    cve_id = record["cveID"]

    # Build readable text for semantic retrieval.
    text_parts = [
        f"{cve_id}: {record.get('vulnerabilityName', '').strip()}",
        f"Vendor: {record.get('vendorProject', '')}",
        f"Product: {record.get('product', '')}",
        f"Description: {record.get('shortDescription', '')}",
        "Status: Listed in CISA's Known Exploited Vulnerabilities catalog.",
    ]

    required_action = record.get("requiredAction")
    if required_action:
        text_parts.append(f"Required action: {required_action}")

    # Keep structured attributes as metadata.
    metadata = {
        "source": "CISA_KEV",
        "cve_id": cve_id,
    }

    field_mapping = {
        "vendorProject": "vendor",
        "product": "product",
        "dateAdded": "date_added",
        "dueDate": "due_date",
        "knownRansomwareCampaignUse": "known_ransomware_use",
        "forensicTriage": "forensic_triage",
    }

    for source_field, target_field in field_mapping.items():
        value = record.get(source_field)
        if value is not None and value != "":
            metadata[target_field] = value

    cwes = record.get("cwes", [])
    if cwes:
        metadata["cwes"] = ", ".join(cwes)

    return {
        "id": f"CISA_KEV:{cve_id}",
        "text": " ".join(text_parts),
        "metadata": metadata,
    }


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as file:
        records = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    if not records:
        raise ValueError("No KEV records found in the input file.")

    documents = [prepare_document(record) for record in records]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        for document in documents:
            file.write(json.dumps(document, ensure_ascii=False) + "\n")

    print("KEV records read:", len(records))
    print("Documents prepared:", len(documents))
    print("Saved documents to:", OUTPUT_PATH)

    print("\nSample prepared document:")
    print(json.dumps(documents[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
