import csv
import base64
import requests
import boto3
import sys
from datetime import timedelta

API_URL = "https://api.mitzimatthew.love"
WALLET_ENDPOINT = f"{API_URL}/wallet/pass/generate"
USER_LIST_ENDPOINT = f"{API_URL}/gizmo/user/list"
OUTPUT_CSV = "passes_to_send.csv"

s3_client = boto3.client("s3")


def get_all_attending_users(internal_api_key):
    """Fetch all users with RSVP status ATTENDING"""
    headers = {"Internal-Api-Key": internal_api_key, "Content-Type": "application/json"}

    try:
        response = requests.get(USER_LIST_ENDPOINT, headers=headers)
        response.raise_for_status()

        data = response.json()
        users = data.get("users", [])

        attending_users = [u for u in users if u.get("rsvp_status") == "ATTENDING"]
        return attending_users
    except Exception as e:
        print(f"❌ Failed to fetch users: {e}")
        raise


def generate_pass_for_user(first_last, internal_api_key):
    """Call wallet Lambda to generate a pass for a user"""
    headers = {"Internal-Api-Key": internal_api_key, "Content-Type": "application/json"}

    try:
        payload = {"first_last": first_last}
        response = requests.post(WALLET_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        pass_data_base64 = data.get("pass_data")

        if not pass_data_base64:
            raise ValueError("No pass_data in response")

        return base64.b64decode(pass_data_base64)
    except requests.HTTPError as http_err:
        print(f"❌ HTTP error for {first_last}: {http_err} - {response.text}")
        raise
    except Exception as e:
        print(f"❌ Error generating pass for {first_last}: {e}")
        raise


def upload_pass_to_s3(first_last, pass_bytes, s3_bucket_name):
    """Upload .pkpass file to S3 and return pre-signed URL"""
    try:
        object_key = f"wallet-passes/{first_last}.pkpass"

        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=object_key,
            Body=pass_bytes,
            ContentType="application/vnd.apple.pkpass"
        )

        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_bucket_name, 'Key': object_key},
            ExpiresIn=int(timedelta(days=7).total_seconds())
        )

        return presigned_url
    except Exception as e:
        print(f"❌ Failed to upload pass for {first_last} to S3: {e}")
        raise


def main():
    """Generate passes for all attending users and output CSV"""
    if len(sys.argv) != 3:
        print("Usage: python generate_wallet_passes.py <internal_api_key> <s3_bucket_name>")
        sys.exit(1)

    internal_api_key = sys.argv[1]
    s3_bucket_name = sys.argv[2]

    print("🦇 Starting Apple Wallet pass generation...")

    attending_users = get_all_attending_users(internal_api_key)
    print(f"✅ Found {len(attending_users)} attending users")

    results = []

    for user in attending_users:
        first_last = f"{user['first']}_{user['last']}"
        phone = user.get("address", {}).get("phone", "")

        if not phone:
            print(f"⚠️  Skipping {first_last} - no phone number")
            continue

        try:
            print(f"⏳ Generating pass for {first_last}...")
            pass_bytes = generate_pass_for_user(first_last, internal_api_key)

            print(f"⏳ Uploading pass for {first_last} to S3...")
            download_url = upload_pass_to_s3(first_last, pass_bytes, s3_bucket_name)

            results.append({
                "first_last": first_last,
                "phone": phone,
                "download_url": download_url
            })

            print(f"✅ Generated pass for {first_last}")

        except Exception as e:
            print(f"❌ Failed to process {first_last}: {e}")
            continue

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["first_last", "phone", "download_url"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Generated {len(results)} passes")
    print(f"📄 Output saved to {OUTPUT_CSV}")
    print(f"🦇 Next step: Review the passes, then run send_wallet_passes.py")


if __name__ == "__main__":
    main()
