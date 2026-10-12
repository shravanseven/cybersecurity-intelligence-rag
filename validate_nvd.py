
import json

file_path = "data/nvd_cves.jsonl"

records = []

# Read and parse each JSON line
with open(file_path, "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        record = json.loads(line)
        records.append(record)

        # Check required fields
        required_fields = ["cve_id", "description", "published"]

        for field in required_fields:
            if field not in record:
                raise ValueError(
                    f"Missing field '{field}' on line {line_number}"
                )

# Check for duplicate CVE IDs
cve_ids = [record["cve_id"] for record in records]
unique_ids = set(cve_ids)

print("Total records:", len(records))
print("Unique CVE IDs:", len(unique_ids))
print("Duplicate IDs:", len(cve_ids) - len(unique_ids))
print("All records have the required fields.")

if records:
    print("\nSample record:")
    print(json.dumps(records[0], indent=4))
