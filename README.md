# Universal Web Scraper (Python)

A configurable, production-ready web scraping framework built in Python.

This project is designed to scrape **any paginated listing website** by defining CSS selectors in a JSON config file — no core code changes required.

It supports:
- Static HTML scraping
- JavaScript-rendered pages (via Playwright fallback)
- Selector-driven parsing
- Proxy rotation and adaptive throttling
- CSV and JSON export
- Clean CLI interface

This repository is intended as a **portfolio project** and a **reusable scraping engine** for real client work.

---

## Key Features

- **Selector-driven parsing**
  - Define what to scrape using JSON configs
  - No hardcoded site logic in Python

- **Hybrid fetching**
  - Requests for fast static pages
  - Automatic Playwright fallback for JS-rendered pages

- **Anti-blocking measures**
  - Proxy rotation (requests)
  - Per-proxy cooldowns
  - Adaptive request throttling
  - Randomized delays

- **Clean architecture**
  - Fetching, parsing, exporting fully decoupled
  - Easy to extend for new sites or features

- **CLI-driven**
  - No code edits required to run against new sites

---

## Project Structure
    universal_scraper/
    ├── main.py # CLI entry point
    ├── fetch.py # Requests-based fetching + retries
    ├── browser_fetch.py # Playwright JS rendering
    ├── smart_fetch.py # Static → JS fallback logic
    ├── parsing.py # Selector-driven parsing engine
    ├── proxy_manager.py # Proxy rotation + cooldowns
    ├── export.py # CSV / JSON exporters
    ├── configs/
    │ └── books_toscrape.json
    └── README.md

---

## Installation Requirements
- Python 3.10+
- pip

## Installation dependencies
    pip install requests beautifulsoup4 playwright
    playwright install

## Usage
    Basic example: 
        python main.py
        --url https://books.toscrape.com/catalogue/page-1.html
        --config configs/books_toscrape.json
        --base-url https://books.toscrape.com/catalogue/
        --output books_demo
        --format both
        --max-pages 5
        --delay 1.5

    Outputs:
        books_demo.csv
        books_demo.json

## Config-Driven Scraping

    Each site is defined by a JSON config file.

    Example: configs/books_toscrape.json

{
    "item_selector": "article.product_pod",
    "fields": {
        "title": { "selector": "h3 a", "attr": "title" },
        "price": { "selector": ".price_color", "text": true },
        "rating": {
        "selector": "p.star-rating",
        "class_exclude": ["star-rating"]
        },
        "url": {
        "selector": "h3 a",
        "attr": "href",
        "absolute": true
        }
    },
    "pagination": {
        "selector": "li.next a",
        "attr": "href",
        "absolute": true
    }
}