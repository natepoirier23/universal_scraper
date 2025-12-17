import requests
import time
import random
from typing import Optional
from proxy_manager import ProxyManager

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

# Example proxy list — replace with real ones later
PROXIES = [
    # "http://user:pass@ip:port",
]

proxy_manager = ProxyManager(PROXIES) if PROXIES else None


def fetch_url(url: str, max_retries: int = 3) -> Optional[str]:
    for attempt in range(1, max_retries + 1):
        proxy = proxy_manager.get_proxy() if proxy_manager else None

        proxies = {"http": proxy, "https": proxy} if proxy else None

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                proxies=proxies,
                timeout=10,
            )

            # Adaptive throttling
            if response.status_code in (429, 503):
                raise requests.HTTPError(f"Rate limited ({response.status_code})")

            response.raise_for_status()
            return response.text

        except Exception as e:
            print(f"[Attempt {attempt}] Fetch failed ({proxy}): {e}")

            if proxy_manager and proxy:
                proxy_manager.mark_bad(proxy)

            if attempt == max_retries:
                return None

            # Adaptive backoff
            wait = random.uniform(1.5, 4.0)
            print(f"Cooling down for {wait:.2f}s...")
            time.sleep(wait)

    return None
