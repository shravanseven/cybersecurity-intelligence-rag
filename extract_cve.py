
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

#CVE ID
cve_id = data["vulnerabilities"][0]["cve"]["id"]

#PUBLICATION DATE
published = None
for item in data["vulnerabilities"][0]["cve"]:
    if item == "published":
        published = data["vulnerabilities"][0]["cve"][item]

#ENGLISH DESCRIPTION
description = None
for item in data["vulnerabilities"][0]["cve"]["descriptions"]:
    if item["lang"] == "en":
        description = item["value"]

cve_record = {
    "cve_id": cve_id,
    "description": description,
    "published": published
}

print(cve_record["published"])