from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, List, Any


def parse_items(html: str, config: Dict[str, Any], base_url: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    items = []

    for block in soup.select(config["item_selector"]):
        record = {}

        for field, rules in config["fields"].items():
            el = block.select_one(rules["selector"])
            if not el:
                record[field] = ""
                continue

            # Attribute extraction
            if "attr" in rules:
                value = el.get(rules["attr"], "").strip()
            # Text extraction
            elif rules.get("text"):
                value = el.get_text(strip=True)
            # Class-based extraction
            elif "class_exclude" in rules:
                classes = el.get("class", [])
                value = next((c for c in classes if c not in rules["class_exclude"]), "")
            else:
                value = el.get_text(strip=True)

            if rules.get("absolute"):
                value = urljoin(base_url, value)

            record[field] = value

        items.append(record)

    return items


def find_next_page(html: str, config: Dict[str, Any], base_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    rules = config.get("pagination")

    if not rules:
        return None

    el = soup.select_one(rules["selector"])
    if not el:
        return None

    href = el.get(rules.get("attr", "href"), "").strip()
    return urljoin(base_url, href)
