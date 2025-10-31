import csv
import requests
import sys

API_URL = "https://api.mitzimatthew.love"
TEXT_ENDPOINT = f"{API_URL}/gizmo/text"
INPUT_CSV = "passes_to_send.csv"

MESSAGE_TEMPLATE = """🎉 Your Wedding Invitation 🎉

Add your digital invitation to Apple Wallet:
{download_url}

See you at the wedding!
"""


def send_pass_text(phone, download_url, internal_api_key):
    """Send text message with Apple Wallet pass download link"""
    headers = {"Internal-Api-Key": internal_api_key, "Content-Type": "application/json"}

    message = MESSAGE_TEMPLATE.format(download_url=download_url)

    payload = {
        "template_type": "RAW_TEXT",
        "template_details": {"raw": message},
        "recipient_phone": phone,
        "is_blast": False
    }

    try:
        response = requests.post(TEXT_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        return True
    except requests.HTTPError as http_err:
        print(f"❌ HTTP error: {http_err} - {response.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Send Apple Wallet passes via SMS to all users in CSV"""
    if len(sys.argv) != 2:
        print("Usage: python send_wallet_passes.py <internal_api_key>")
        sys.exit(1)

    internal_api_key = sys.argv[1]

    print("🦇 Starting to send Apple Wallet passes...")

    try:
        with open(INPUT_CSV, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"❌ File {INPUT_CSV} not found. Run generate_wallet_passes.py first.")
        sys.exit(1)

    print(f"✅ Found {len(rows)} passes to send")

    successes = 0
    failures = 0

    for row in rows:
        first_last = row["first_last"]
        phone = row["phone"]
        download_url = row["download_url"]

        print(f"⏳ Sending pass to {first_last} ({phone})...")

        if send_pass_text(phone, download_url, internal_api_key):
            print(f"✅ Sent to {first_last}")
            successes += 1
        else:
            print(f"❌ Failed to send to {first_last}")
            failures += 1

    print(f"\n✅ Successfully sent {successes} passes")
    print(f"❌ Failed to send {failures} passes")
    print("🦇 Mission complete.")


if __name__ == "__main__":
    main()
