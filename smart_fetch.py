from fetch import fetch_url
from browser_fetch import fetch_rendered_html
from bs4 import BeautifulSoup

def smart_fetch(url: str) -> str | None:
    """
    Fetch a URL using static requests first.
    If content is missing, JS-rendered, or anti-bot,
    retry using Playwright.
    """

    html = fetch_url(url)
    html += "<!-- captcha -->"

    if html is None:
        print("[smart_fetch] Static fetch failed; using Playwright...")
        return fetch_rendered_html(url)

    soup = BeautifulSoup(html, "html.parser")
    text_content = soup.get_text(strip=True)
    lower_html = html.lower()

    # --- Anti-bot detection ---
    anti_bot_signals = [
        "captcha", "verify you are human", "unusual traffic",
        "access denied", "forbidden", "cloudflare", "attention required",
    ]
    if any(signal in lower_html for signal in anti_bot_signals):
        print("[smart_fetch] Anti-bot page detected; switching to Playwright...")
        return fetch_rendered_html(url)

    # --- JS-rendered detection: script-heavy DOM ---
    script_count = len(soup.find_all("script"))
    tag_count = len(soup.find_all())

    if script_count > 5 and tag_count < 30:
        print("[smart_fetch] Script-heavy, low-content page detected; using Playwright...")
        return fetch_rendered_html(url)

    # --- Specific detection for quotes.toscrape.com/js/ ---
    if "quotes to scrape" in lower_html and not soup.select(".quote"):
        print("[smart_fetch] JS-only quotes page detected; using Playwright...")
        return fetch_rendered_html(url)

    # --- If we reach this point, static HTML is meaningful ---
    return html