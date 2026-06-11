import json
import os

import boto3

S3_CLIENT = boto3.client("s3")
SES_S3_BUCKET_NAME = os.environ["ses_s3_bucket_name"]


def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    records = event.get("Records") or []
    if not records or "Sns" not in records[0]:
        print("Skipping event with no SNS record")
        return None

    sns = records[0]["Sns"]
    message = sns.get("Message", "")
    key = sns.get("MessageId")
    if not key:
        print("Skipping SNS record with no MessageId")
        return None

    print("From SNS: " + message)

    S3_CLIENT.put_object(
        Bucket=SES_S3_BUCKET_NAME,
        Key=key,
        Body=message,
        ContentType="application/json",
    )

    return message
