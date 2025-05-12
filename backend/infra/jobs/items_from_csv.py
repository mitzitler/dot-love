import csv
import requests
from decimal import Decimal

API_URL = "https://api.mitzimatthew.love/spectaculo/item"
HEADERS = {"X-First-Last": "matthew_saucedo", "Content-Type": "application/json"}


def parse_date(date_str):
    if not date_str:
        return None
    parts = date_str.strip().split("/")
    if len(parts) != 3:
        return None
    month, day, year = parts
    return f"{month.zfill(2)}/{day.zfill(2)}/{year}"


def parse_bool(value):
    return str(value).strip().lower() == "true"


with open("registry_items.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            payload = {
                "name": row.get("name", "").strip(),
                "last_checked": parse_date(row.get("last_checked", "")),
                "brand": row.get("brand", "").strip(),
                "descr": row.get("descr", "").strip(),
                "size_score": float(Decimal(row.get("size_score", "0.0").strip())),
                "art_score": float(Decimal(row.get("art_score", "0.0").strip())),
                "link": row.get("link", "").strip(),
                "img_url": row.get("image_name", "").strip(),
                "price_cents": int(float(row.get("price_cents", 0))),
            }

            response = requests.post(API_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            print(f"✅ Uploaded: {payload['name']}")
        except requests.HTTPError as http_err:
            print(f"❌ HTTP error for {row.get('name')}: {http_err} - {response.text}")
        except Exception as err:
            print(f"❌ Error processing {row.get('name')}: {err}")
