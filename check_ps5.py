import os
import sys
import requests

URL = "https://www.playstation.com/it-it/ps5/ps5-pro/buy-now/product/PSD001-PSDE01942_39-PS5PROCHASASIRSE/"
BUY = "https://direct.playstation.com/it-it/buy-consoles/playstation5-pro-console-2-tb"
STATE_FILE = "state.txt"

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9",
}
ESAURITO = ("Non disponibile per l'acquisto", "Scorte attualmente esaurite")


def telegram(testo):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": testo},
        timeout=15,
    )
    r.raise_for_status()


def is_available(html):
    # pagina valida (c'è il prodotto) e nessuna scritta di esaurito
    return "PlayStation" in html and "Pro" in html and not any(t in html for t in ESAURITO)


def read_state():
    try:
        return open(STATE_FILE).read().strip()
    except FileNotFoundError:
        return "unavailable"


def main():
    r = requests.get(URL, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        # es. 403 anti-bot: non cambio lo stato, segnalo l'errore nel log
        print(f"HTTP {r.status_code}, controllo saltato")
        sys.exit(1)

    new = "available" if is_available(r.text) else "unavailable"
    old = read_state()
    print(f"stato: {old} -> {new}")

    if new == "available" and old != "available":
        telegram(f"🎮 PS5 Pro disponibile!\n{BUY}")
    open(STATE_FILE, "w").write(new)


if __name__ == "__main__":
    main()
