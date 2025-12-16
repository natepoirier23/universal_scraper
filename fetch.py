import random
import time
from typing import Optional

import requests

# Custom headers to look like a real browser.
# Helps reduce trivial bot blocking and serves as good practice.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_url(
    url: str,
    max_retries: int = 3,
    backoff_factor: float = 1.5,
) -> Optional[str]:
    """
    Attempt to fetch a URL with:
    - custom headers
    - retry logic
    - exponential backoff + jitter

    Returns:
        HTML text on success, or None if all attempts fail.
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=10, headers=HEADERS)
            response.raise_for_status()
            return response.text  # Successful response

        except requests.RequestException as e:
            print(f"[Attempt {attempt}] Request failed for {url}: {e}")

            # If not the last attempt, sleep before retrying
            if attempt < max_retries:
                sleep_time = backoff_factor ** attempt + random.uniform(0, 0.5)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)

    # All attempts exhausted
    print(f"Failed to fetch {url} after {max_retries} attempts.")
    return None
