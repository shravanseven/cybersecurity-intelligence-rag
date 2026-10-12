
import json
import os
from urllib.request import urlopen
from urllib.parse import urlencode


base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"

results_per_page = 5
start_index = 0
max_pages = 3
pages_fetched = 0

cve_records = []

while pages_fetched < max_pages:
    params = {
        "resultsPerPage": results_per_page,
        "startIndex": start_index
    }

    url = f"{base_url}?{urlencode(params)}"

    with urlopen(url, timeout=30) as response:
        data = json.load(response)

    vulnerabilities = data["vulnerabilities"]

    for item in vulnerabilities:
        cve = item["cve"]

        # Extract CVE ID
        cve_id = cve["id"]

        # Extract English description
        description = None
        for desc in cve.get("descriptions", []):
            if desc["lang"] == "en":
                description = desc["value"]
                break

        # Extract publication date
        published = cve.get("published")

        # Create normalized record
        cve_record = {
            "cve_id": cve_id,
            "description": description,
            "published": published
        }

        # Add record to our dataset
        cve_records.append(cve_record)

    start_index += results_per_page
    pages_fetched += 1

    if start_index >= data["totalResults"]:
        break

# Create the data directory if it does not exist
os.makedirs("data", exist_ok=True)

# Save each CVE record as one JSON line
with open("data/nvd_cves.jsonl", "w", encoding="utf-8") as file:
    for record in cve_records:
        file.write(json.dumps(record) + "\n")

print(f"Saved {len(cve_records)} CVE records to data/nvd_cves.jsonl")


print("Total CVE records collected:", len(cve_records))
print("First CVE record:")
print(json.dumps(cve_records[0], indent=4))
