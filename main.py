import argparse
import random
import time
import json
from parsing import parse_items, find_next_page, parse_detail_page, parse_table_by_header
from export import write_to_csv, write_to_json
from smart_fetch import smart_fetch

BASE_URL = "https://books.toscrape.com/catalogue/"


def parse_cli_args():
    parser = argparse.ArgumentParser(description="Universal web scraper")

    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="Starting URL to scrape",
    )

    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to site config JSON file",
    )

    parser.add_argument(
        "--base-url",
        type=str,
        required=True,
        help="Base URL for resolving relative links",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output filename prefix (default: output)",
    )

    parser.add_argument(
        "--format",
        choices=["csv", "json", "both"],
        default="csv",
        help="Output format",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=200,
        help="Maximum number of pages to scrape",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Base delay (seconds) between page requests",
    )

    return parser.parse_args()

def main():
    args = parse_cli_args()

    records: list[dict] = []
    page_counter = 0
    next_url = args.url

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    BASE_URL = args.base_url

    while next_url:
        print(f"Scraping: {next_url}")

        html = smart_fetch(next_url)
        if html is None:
            print("Failed to retrieve page; stopping.")
            break

        # --- LIST PAGE PARSING ---
        items = parse_items(html, config, BASE_URL)
        print(f"  Found {len(items)} items")

        if not items:
            print("No items found; site structure may differ.")
            break

        # --- DETAIL PAGE PARSING (OPTIONAL, CONFIG-DRIVEN) ---
        detail_fields = config.get("detail_fields")

        for item in items:
            # If this site has no detail fields, skip detail scraping entirely
            if not detail_fields:
                break

            detail_url = item.get("url")
            if not detail_url:
                continue

            detail_html = smart_fetch(detail_url)
            if detail_html is None:
                print(f"[WARN] Failed to fetch detail page: {detail_url}")
                continue

            detail_data = parse_detail_page(detail_html, detail_fields)
            table_data = parse_table_by_header(detail_html)

            item.update(table_data)
            item.update(detail_data)

            # Polite delay between detail-page requests
            time.sleep(random.uniform(0.5, 1.2))

        records.extend(items)

        # --- PAGINATION ---
        next_url = find_next_page(html, config, BASE_URL)

        jitter = random.uniform(0.5, 1.5)
        time.sleep(args.delay * jitter)

        page_counter += 1
        if page_counter >= args.max_pages:
            print("Reached max_pages; stopping.")
            break

    print(f"Total items collected: {len(records)}")

    if args.format in ("csv", "both"):
        write_to_csv(records, f"{args.output}.csv")

    if args.format in ("json", "both"):
        write_to_json(records, f"{args.output}.json")

if __name__ == "__main__":
    main()
