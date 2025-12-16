import argparse
import random
import time
import json
from parsing import parse_items, find_next_page
from export import write_to_csv, write_to_json
from smart_fetch import smart_fetch

START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_PAGES = 200
BASE_URL = "https://books.toscrape.com/catalogue/"


def parse_cli_args():
    parser = argparse.ArgumentParser(description="Universal web scraper")
    parser.add_argument("--url", type=str, help="Starting URL")
    parser.add_argument(
        "--format",
        choices=["csv", "json", "both"],
        default="csv",
        help="Output format",
    )
    return parser.parse_args()


def main():
    args = parse_cli_args()

    records: list[dict] = []
    page_counter = 0
    next_url = args.url if args.url else START_URL

    with open("configs/books_toscrape.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    while next_url:
        print(f"Scraping: {next_url}")

        html = smart_fetch(next_url)
        if html is None:
            print("Failed to retrieve page; stopping.")
            break

        items = parse_items(html, config, BASE_URL)
        print(f"  Found {len(items)} items")

        if not items:
            print("No items found; site structure may differ.")
            break

        records.extend(items)

        next_url = find_next_page(html, config, BASE_URL)

        delay = random.uniform(1.0, 2.0)
        time.sleep(delay)

        page_counter += 1
        if page_counter >= MAX_PAGES:
            print("Reached MAX_PAGES; stopping.")
            break

    print(f"Total items collected: {len(records)}")

    if args.format in ("csv", "both"):
        write_to_csv(records, "output.csv")

    if args.format in ("json", "both"):
        write_to_json(records, "output.json")


if __name__ == "__main__":
    main()
