
import json
import os
from urllib.request import urlopen


URL = (
    "https://www.cisa.gov/sites/default/files/feeds/"
    "known_exploited_vulnerabilities.json"
)

OUTPUT_PATH = "data/kev_vulnerabilities.jsonl"


def main():
    # 1. Download and parse the CISA KEV catalog
    with urlopen(URL, timeout=30) as response:
        catalog = json.load(response)

    vulnerabilities = catalog.get("vulnerabilities", [])

    # 2. Display basic catalog information
    print("Catalog version:", catalog.get("catalogVersion"))
    print("Release date:", catalog.get("dateReleased"))
    print("Declared CVE count:", catalog.get("count"))
    print("Actual CVE count:", len(vulnerabilities))

    if catalog.get("count") != len(vulnerabilities):
        raise ValueError("Declared count does not match actual record count.")

    # 3. Save each vulnerability as a separate JSONL record
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        for vulnerability in vulnerabilities:
            file.write(
                json.dumps(vulnerability, ensure_ascii=False) + "\n"
            )

    print("Saved raw KEV records to:", OUTPUT_PATH)

    # 4. Display one sample to inspect the saved data structure
    if vulnerabilities:
        print("\nFirst vulnerability record:")
        print(json.dumps(vulnerabilities[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
