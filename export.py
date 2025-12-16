import csv
import json
from typing import List, Dict, Any


def write_to_csv(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Write a list of dictionaries to a CSV file.

    Fieldnames are inferred dynamically from the first record.
    """
    if not data:
        print("[export] No data to write to CSV.")
        return

    fieldnames = sorted(data[0].keys())

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"[export] Wrote {len(data)} rows to {filename}")


def write_to_json(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Write a list of dictionaries to a JSON file.
    """
    if not data:
        print("[export] No data to write to JSON.")
        return

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[export] Wrote {len(data)} records to {filename}")
