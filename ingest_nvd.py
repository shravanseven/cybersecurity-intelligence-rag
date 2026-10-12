
import json
import os
import time
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError

BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

RESULTS_PER_PAGE = 5
MAX_PAGES = 3
MAX_RETRIES = 3


def fetch_page(start_index):
    """Fetch one page from NVD, retrying temporary failures."""

    params = {
        "resultsPerPage": RESULTS_PER_PAGE,
        "startIndex": start_index,
    }
    url = f"{BASE_URL}?{urlencode(params)}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urlopen(url, timeout=30) as response:
                data = json.load(response)

            # Check the response has the expected structure
            if not isinstance(data.get("vulnerabilities"), list):
                raise ValueError("Unexpected NVD response structure")

            if "totalResults" not in data:
                raise ValueError("NVD response is missing totalResults")

            return data

        except HTTPError as error:
            # Retry temporary server errors and rate limiting
            if error.code in (403, 429, 503) and attempt < MAX_RETRIES:
                wait = 5 * attempt
                print(
                    f"HTTP {error.code}; retrying in {wait} seconds "
                    f"(attempt {attempt}/{MAX_RETRIES})"
                )
                time.sleep(wait)
                continue

            raise RuntimeError(
                f"NVD returned HTTP {error.code}: {error.reason}"
            ) from error

        except (URLError, TimeoutError) as error:
            if attempt < MAX_RETRIES:
                wait = 2 * attempt
                print(
                    f"Network error; retrying in {wait} seconds "
                    f"(attempt {attempt}/{MAX_RETRIES})"
                )
                time.sleep(wait)
                continue

            raise RuntimeError(
                f"NVD request failed after {MAX_RETRIES} attempts: {error}"
            ) from error

        except json.JSONDecodeError as error:
            raise RuntimeError("NVD returned invalid JSON") from error

    raise RuntimeError("Could not fetch the NVD page")


def main():
    cve_records = []
    start_index = 0
    pages_fetched = 0
    total_results = None

    while pages_fetched < MAX_PAGES:
        print(f"Fetching page starting at index {start_index}...")

        data = fetch_page(start_index)
        vulnerabilities = data["vulnerabilities"]
        total_results = data["totalResults"]

        for item in vulnerabilities:
            cve = item.get("cve", {})

            description = None
            for desc in cve.get("descriptions", []):
                if desc.get("lang") == "en":
                    description = desc.get("value")
                    break

            cve_records.append({
                "cve_id": cve.get("id"),
                "description": description,
                "published": cve.get("published"),
            })

        pages_fetched += 1
        start_index += RESULTS_PER_PAGE

        if not vulnerabilities or start_index >= total_results:
            break

        # Be considerate of the public API's request limits
        time.sleep(6)

    # Do not save if the fetching process failed before reaching here.
    if not cve_records:
        raise RuntimeError("No CVE records were collected")

    # Write to a temporary file first, then replace the previous dataset.
    os.makedirs("data", exist_ok=True)
    temp_path = "data/nvd_cves.jsonl.tmp"
    output_path = "data/nvd_cves.jsonl"

    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            for record in cve_records:
                file.write(json.dumps(record) + "\n")

        os.replace(temp_path, output_path)

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    print(f"\nPages fetched: {pages_fetched}")
    print(f"Total CVE records collected: {len(cve_records)}")
    print(f"Saved dataset to {output_path}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError) as error:
        print(f"\nIngestion failed: {error}")
        raise SystemExit(1)
