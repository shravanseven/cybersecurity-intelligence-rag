
import json
from urllib.request import urlopen
from urllib.parse import urlencode

base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"

params = {
    "cveId": "CVE-2021-44228"
}

url = f"{base_url}?{urlencode(params)}"

with urlopen(url, timeout=30) as response:
    data = json.load(response)

print("Total results:", data["totalResults"])

vulnerability = data["vulnerabilities"][0]["cve"]

print("CVE ID:", vulnerability["id"])

description = next(
    item["value"]
    for item in vulnerability["descriptions"]
    if item["lang"] == "en"
)

print("Description:", description)