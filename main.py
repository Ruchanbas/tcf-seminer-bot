import os
import json
import requests
from bs4 import BeautifulSoup

URL = "https://www.tcf.gov.tr/faaliyetler/"
FILTER_CATEGORY = "Seminer"
FILTER_BRANCH = "Pilates"
FILTER_CITIES = ["Ankara", "İstanbul"]
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SEEN_FILE = "seen_seminars.json"


def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram bilgileri eksik.")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data, timeout=30)
    response.raise_for_status()
    print("Telegram mesajı gönderildi.")


def get_html():
    headers = {"User-Agent": "Mozilla/5.0"}
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
        items.append({
            "kategori": clean_text(cols[1].get_text(" ", strip=True)),
            "baslik":   clean_text(cols[2].get_text(" ", strip=True)),
            "brans":    clean_text(cols[3].get_text(" ", strip=True)),
            "yer":      clean_text(cols[4].get_text(" ", strip=True)),
            "tarih":    clean_text(cols[5].get_text(" ", strip=True)),
        })
    return items


def filter_items(items):
    result = []
    for item in items:
        if FILTER_CATEGORY.lower() not in item["kategori"].lower():
            continue
        if (FILTER_BRANCH.lower() not in item["brans"].lower() and
                FILTER_BRANCH.lower() not in item["baslik"].lower()):
            continue
        combined = f"{item['yer']} {item['baslik']}".lower()
        if not any(city.lower() in combined for city in FILTER_CITIES):
            continue
        result.append(item)
    return result


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)


def make_uid(item):
    return f"{item['baslik']}|{item['tarih']}|{item['yer']}"


def main():
    seen = load_seen()

    html = get_html()
    items = parse(html)
    filtered = filter_items(items)

    new_items = [(make_uid(i), i) for i in filtered if make_uid(i) not in seen]

    if not new_items:
        print("Yeni seminer bulunamadı.")
        return

    for uid, item in new_items:
        message = (
            "🏋️ <b>Yeni Pilates Semineri!</b>\n\n"
            f"📌 <b>Başlık:</b> {item['baslik']}\n"
            f"📍 <b>Yer:</b> {item['yer']}\n"
            f"📅 <b>Tarih:</b> {item['tarih']}"
        )
        print(message)
        send_telegram(message)
        seen.add(uid)

    save_seen(seen)
    print(f"{len(new_items)} yeni seminer gönderildi.")


if __name__ == "__main__":
    main()
