import json
import boto3

S3_CLIENT = boto3.client("s3")
SES_S3_BUCKET_NAME = os.environ["ses_s3_bucket_name"]


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    message = event["Records"][0]["Sns"]["Message"]
    print("From SNS: " + message)

    # S3_CLIENT.put_object(
    # Bucket=SES_S3_BUCKET_NAME, Key=key, Body=email.encode("utf-8")
    # )

    return message
