# tcf-seminer-bot

**Zero-infrastructure monitoring bot.** Watches the [Turkish Gymnastics Federation events page](https://www.tcf.gov.tr/faaliyetler/) and sends a Telegram notification when a new **Pilates seminar** is announced in **Ankara or İstanbul**.

No servers, no cloud bill: the whole thing is a single Python script scheduled with **GitHub Actions**.

## How it works

```
GitHub Actions (cron)
   └─► main.py
        1. fetch the events page (requests)
        2. parse the announcements table (BeautifulSoup)
        3. filter: branch = Pilates, city ∈ {Ankara, İstanbul}
        4. dedupe against seen_seminars.json (title|date|venue as UID)
        5. push new items to Telegram (Bot API, HTML-formatted message)
```

Deduplication means the bot can run as often as you like — you only get a message when something *new* appears.

## Setup

1. Create a Telegram bot with [@BotFather](https://t.me/BotFather) and note the token
2. Get your chat ID (message the bot, then check `getUpdates`)
3. Add both as repository secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
4. The scheduled workflow in `.github/workflows/` does the rest

Run locally:

```bash
pip install -r requirements.txt
TELEGRAM_BOT_TOKEN=xxx TELEGRAM_CHAT_ID=yyy python main.py
```

## Customizing

Filters are constants at the top of `main.py`:

```python
FILTER_CATEGORY = "Seminer"
FILTER_BRANCH   = "Pilates"
FILTER_CITIES   = ["Ankara", "İstanbul"]
```

Change the branch or cities and the same bot monitors any other federation activity.

## Stack

`Python` · `requests` · `BeautifulSoup` · `GitHub Actions` · `Telegram Bot API`
