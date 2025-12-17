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

def parse_detail_page(html: str, detail_fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a detail page using selector rules.
    """
    soup = BeautifulSoup(html, "html.parser")
    record = {}

    for field, rules in detail_fields.items():
        el = soup.select_one(rules["selector"])
        if not el:
            record[field] = ""
            continue

        if "attr" in rules:
            value = el.get(rules["attr"], "").strip()
        elif rules.get("text"):
            value = el.get_text(strip=True)
        else:
            value = el.get_text(strip=True)

        record[field] = value

    return record

def parse_table_by_header(html: str) -> dict:
    """
    Parse key-value tables where <th> is the field name and <td> is the value.
    """
    soup = BeautifulSoup(html, "html.parser")
    data = {}

    for row in soup.select("table.table-striped tr"):
        th = row.find("th")
        td = row.find("td")

        if not th or not td:
            continue

        key = th.get_text(strip=True).lower().replace(" ", "_")
        value = td.get_text(strip=True)

        data[key] = value

    return data
