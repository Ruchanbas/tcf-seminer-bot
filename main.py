import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.tcf.gov.tr/faaliyetler/"

FILTER_CATEGORY = "Seminer"
FILTER_BRANCH = "Pilates"
FILTER_CITIES = ["Ankara", "İstanbul"]

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=data, timeout=30)
    response.raise_for_status()


def get_html():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def clean_text(text):
    return " ".join(text.split()).strip()


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table tbody tr")
    items = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        kategori = clean_text(cols[1].get_text(" ", strip=True))
        baslik = clean_text(cols[2].get_text(" ", strip=True))
        brans = clean_text(cols[3].get_text(" ", strip=True))
        yer = clean_text(cols[4].get_text(" ", strip=True))
        tarih = clean_text(cols[5].get_text(" ", strip=True))

        items.append({
            "kategori": kategori,
            "baslik": baslik,
            "brans": brans,
            "yer": yer,
            "tarih": tarih,
        })

    return items


def filter_items(items):
    result = []

    for item in items:
        kategori_text = item["kategori"].lower()
        brans_text = item["brans"].lower()
        baslik_text = item["baslik"].lower()
        yer_text = item["yer"].lower()
        combined_text = f"{yer_text} {baslik_text}"

        if FILTER_CATEGORY.lower() not in kategori_text:
            continue

        if FILTER_BRANCH.lower() not in brans_text and FILTER_BRANCH.lower() not in baslik_text:
            continue

        if not any(city.lower() in combined_text for city in FILTER_CITIES):
            continue

        result.append(item)

    return result


def main():
    html = get_html()
    items = parse(html)
    filtered = filter_items(items)

    if not filtered:
        print("Uygun kayıt yok")
        return

    for item in filtered:
        message = (
            "Yeni Pilates Semineri!\n\n"
            f"Başlık: {item['baslik']}\n"
            f"Yer: {item['yer']}\n"
            f"Tarih: {item['tarih']}"
        )
        print(message)
        send_telegram(message)


if __name__ == "__main__":
    main()
