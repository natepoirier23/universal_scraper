from playwright.sync_api import sync_playwright
import time
import random

def fetch_rendered_html(url: str, wait_selector: str = None, delay: float = 0.0) -> str | None:
    """
    Fetch fully rendered HTML of a JS-driven page using Playwright.
    Includes:
    - realistic user-agent + viewport
    - optional selector wait
    - optional post-load delay
    - proper cleanup on exceptions
    """

    try:
        with sync_playwright() as p:

            # --- RANDOMIZE USER AGENT + VIEWPORT ---
            ua_list = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
                "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.6099.224 Safari/537.36",
            ]

            context = p.chromium.launch(headless=True).new_context(
                user_agent=random.choice(ua_list),
                viewport={
                    "width": random.randint(1200, 1600),
                    "height": random.randint(700, 900),
                },
                bypass_csp=True,  # Helps with restrictive sites
            )

            page = context.new_page()

            # --- NAVIGATION ---
            try:
                page.goto(url, timeout=25000, wait_until="networkidle")
            except Exception as nav_err:
                page.screenshot(path="error_nav.png")
                print(f"[Playwright] Navigation error: {nav_err} (screenshot saved)")
                context.close()
                return None

            # --- OPTIONAL WAIT FOR CONTENT ---
            if wait_selector:
                try:
                    page.wait_for_selector(wait_selector, timeout=12000)
                except Exception:
                    print(f"[Playwright] Selector '{wait_selector}' not found; continuing anyway.")

            # --- OPTIONAL POST-LOAD DELAY ---
            if delay > 0:
                time.sleep(delay)

            # --- GET CONTENT ---
            html = page.content()

            # --- CLEANUP ---
            context.close()
            return html

    except Exception as e:
        print(f"[Playwright] Failed to fetch {url}: {e}")
        return None
