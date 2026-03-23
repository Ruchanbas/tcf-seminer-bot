import json
import requests
from bs4 import BeautifulSoup

URL = "https://www.tcf.gov.tr/faaliyetler/"

FILTER_CATEGORY = "Seminer"
FILTER_BRANCH = "Pilates"
FILTER_CITIES = ["Ankara", "İstanbul"]

def get_html():
    return requests.get(URL).text

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table tbody tr")
    items = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        item = {
            "kategori": cols[1].text.strip(),
            "baslik": cols[2].text.strip(),
            "brans": cols[3].text.strip(),
            "yer": cols[4].text.strip(),
            "tarih": cols[5].text.strip(),
        }

        items.append(item)

    return items

def filter_items(items):
    result = []
    for item in items:
        if item["kategori"] != FILTER_CATEGORY:
            continue

        if "pilates" not in item["brans"].lower() and "pilates" not in item["baslik"].lower():
            continue

        if not any(city.lower() in item["yer"].lower() for city in FILTER_CITIES):
            continue

        result.append(item)

    return result

def main():
    html = get_html()
    items = parse(html)
    filtered = filter_items(items)

    print("Bulunanlar:")
    for i in filtered:
        print(i)

if __name__ == "__main__":
    main()
