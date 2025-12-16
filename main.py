import argparse
import random
import time

from fetch import fetch_url
from parsing import extract_books, extract_next_page_url, extract_book_details
from export import write_books_to_csv, write_books_to_json
from smart_fetch import smart_fetch

START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_PAGES = 200

def parse_cli_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Scrape provided URL.")
    
    parser.add_argument(
        "--url",
        type=str,
        required=False,
        help="Target URL to scrape. Overrides default START_URL if provided.",
    )

    parser.add_argument(
        "--format",
        choices=["csv", "json", "both"],
        default="csv",
        help="Output format for scraped data",
    )

    return parser.parse_args()


def main():
    args = parse_cli_args()

    all_books: list[dict] = []
    page_counter = 0

    next_url = args.url if args.url else START_URL

    while next_url:
        print(f"Scraping: {next_url}")

        html = smart_fetch(next_url)
        if html is None:
            print("Failed to retrieve page; stopping crawl.")
            break

        books = extract_books(html)
        print(f"  Found {len(books)} books on this page.")

        if not books:
            print("No books found. This URL may not match expected site structure.")
            break

        # Detail page scraping
        for book in books:
            detail_url = book["url"]
            detail_html = smart_fetch(detail_url)

            if detail_html is None:
                print(f"[WARN] Failed to fetch detail page: {detail_url}")
                continue

            detail_data = extract_book_details(detail_html)
            book.update(detail_data)

            time.sleep(random.uniform(0.5, 1.2))

        all_books.extend(books)

        # Pagination
        next_url = extract_next_page_url(html)

        # Validate next URL
        if next_url and not next_url.startswith("http"):
            print("Next page URL invalid for current domain; stopping.")
            break

        delay = random.uniform(1.0, 2.0)
        print(f"Sleeping {delay:.2f}s before next request...")
        time.sleep(delay)

        page_counter += 1
        if page_counter >= MAX_PAGES:
            print("Reached MAX_PAGES limit; stopping to avoid infinite loop.")
            break

    print(f"Total books collected: {len(all_books)}")

    if args.format in ("csv", "both"):
        write_books_to_csv(all_books, "books.csv")

    if args.format in ("json", "both"):
        write_books_to_json(all_books, "books.json")


if __name__ == "__main__":
    main()
