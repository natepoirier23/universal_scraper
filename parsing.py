from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Base URL to resolve relative book detail links and next-page links.
BASE_SITE = "https://books.toscrape.com/catalogue/"


def extract_books(html: str) -> list[dict]:
    """
    Parse a page of book listings and return a list of dictionaries with:
    - title
    - price
    - rating
    - url (absolute detail page URL)
    """
    soup = BeautifulSoup(html, "html.parser")

    # Each book card is <article class="product_pod">
    book_elements = soup.select("article.product_pod")

    books: list[dict] = []

    for book in book_elements:
        # Title + relative URL live in <h3><a ...></a></h3>
        link_tag = book.select_one("h3 a")
        if not link_tag:
            # Defensive: skip malformed entries
            continue

        title = link_tag.get("title", "").strip()
        relative_href = link_tag.get("href", "").strip()

        # Convert relative URL to absolute
        url = urljoin(BASE_SITE, relative_href)

        # Price: <p class="price_color">£51.77</p>
        price_tag = book.select_one(".price_color")
        price = price_tag.text.strip() if price_tag else ""

        # Rating encoded as CSS class on <p class="star-rating Three">
        rating_tag = book.select_one("p.star-rating")
        rating = ""
        if rating_tag:
            classes = rating_tag.get("class", [])
            # Remove the generic 'star-rating' class, leaving only the word rating.
            rating_classes = [c for c in classes if c != "star-rating"]
            rating = rating_classes[0] if rating_classes else ""

        books.append(
            {
                "title": title,
                "price": price,
                "rating": rating,
                "url": url,
            }
        )

    return books


def extract_next_page_url(html: str) -> Optional[str]:
    """
    Detect and return the absolute URL for the next paginated page.

    The markup looks like:
        <li class="next"><a href="page-2.html">next</a></li>

    Returns:
        Absolute URL to next page, or None if no further pages exist.
    """
    soup = BeautifulSoup(html, "html.parser")

    next_link = soup.select_one("li.next a")
    if not next_link:
        return None

    relative_href = next_link.get("href", "").strip()
    if not relative_href:
        return None

    return urljoin(BASE_SITE, relative_href)

def extract_book_details(html: str) -> dict:
    """
    Parse the detail page HTML of a single book and extract
    structured metadata such as UPC, description, availability, etc.
    """
    soup = BeautifulSoup(html, "html.parser")
    details = {}

    # --- Extract table-based product information ---
    table = soup.select_one("table.table-striped")
    if table:
        rows = table.select("tr")
        for row in rows:
            header = row.select_one("th").text.strip()
            value = row.select_one("td").text.strip()

            # Normalize table keys to lowercase + underscores
            key = header.lower().replace(" ", "_")
            details[key] = value

    # --- Extract product description ---
    desc_section = soup.select_one("#product_description")
    if desc_section:
        # The paragraph immediately following the description header
        desc_p = desc_section.find_next("p")
        if desc_p:
            details["description"] = desc_p.text.strip()
        else:
            details["description"] = ""
    else:
        details["description"] = ""

    # --- Extract book category ---
    breadcrumb = soup.select("ul.breadcrumb li")
    if len(breadcrumb) >= 3:
        # The last <li> before the active one is the category link
        category_li = breadcrumb[-2]
        details["category"] = category_li.text.strip()
    else:
        details["category"] = ""

    return details
