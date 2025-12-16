import csv
import json


def write_books_to_csv(books: list[dict], filename: str = "books.csv") -> None:
    """
    Write the list of books to a CSV file.
    Ensures that all keys across every book are included as columns.
    """
    if not books:
        print("No books to write (CSV).")
        return

    # Collect all unique keys across all dicts
    fieldnames = set()
    for book in books:
        fieldnames.update(book.keys())
    fieldnames = sorted(fieldnames)  # sort for consistent output

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(books)

    print(f"Wrote {len(books)} rows to {filename}")

def write_books_to_json(books: list[dict], filename: str = "books.json") -> None:
    """
    Write the list of books to a JSON file in a human-readable format.
    """
    if not books:
        print("No books to write (JSON).")
        return

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=4)

    print(f"Wrote {len(books)} rows to {filename}")
