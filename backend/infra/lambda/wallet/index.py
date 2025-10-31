import json
import os
import base64
import hashlib
from enum import Enum

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.event_handler.api_gateway import (
    APIGatewayHttpResolver,
)

INTERNAL_API_KEY = os.environ["internal_api_key"]
USER_TABLE_NAME = os.environ["user_table_name"]
PASS_TYPE_ID = os.environ["pass_type_id"]
TEAM_IDENTIFIER = os.environ["team_identifier"]
APPLE_CERT_BASE64 = os.environ.get("apple_cert_base64")
APPLE_CERT_PASSWORD = os.environ.get("apple_cert_password")
WWDR_CERT_BASE64 = os.environ.get("wwdr_cert_base64")
WEDDING_DETAILS = json.loads(os.environ["wedding_details"])

log = Logger(service="wallet")
app = APIGatewayHttpResolver()

dynamodb_client = boto3.client("dynamodb")


class RsvpStatus(Enum):
    UNDECIDED = 1
    ATTENDING = 2
    NOTATTENDING = 3

    def __str__(self):
        return self.name


def validate_internal_route(event):
    """Validate that the request has a valid Internal-Api-Key header"""
    api_key = event.headers.get("Internal-Api-Key") or event.headers.get(
        "internal-api-key"
    )

    if not api_key or api_key != INTERNAL_API_KEY:
        return Response(
            status_code=401,
            content_type="application/json",
            body={"message": "no valid api key"},
        )
    return None


def get_user_from_db(first_last):
    """Fetch user from DynamoDB by first_last key"""
    try:
        key_expression = {"first_last": {"S": first_last.lower()}}
        response = dynamodb_client.get_item(TableName=USER_TABLE_NAME, Key=key_expression)

        if "Item" not in response:
            return None

        return response["Item"]
    except Exception as e:
        log.exception(f"Failed to fetch user {first_last} from database")
        raise


def create_pass_for_user(user_data, table_number=None):
    """
    Generate an Apple Wallet pass for a wedding guest.

    NOTE: This currently returns JSON placeholder data until Apple certificates are configured.
    Once certificates are in Secrets Manager, this will use passkit-generator to create
    and sign actual .pkpass files.
    """
    first_last = user_data["first_last"]["S"]
    first_name = first_last.split("_")[0].capitalize()
    last_name = first_last.split("_")[1].capitalize()
    rsvp_status = user_data["rsvp_status"]["S"]

    if rsvp_status != "ATTENDING":
        raise ValueError(f"User {first_last} is not attending (status: {rsvp_status})")

    has_plus_one = user_data.get("date_link_requested", {}).get("BOOL", False)
    guest_pair = user_data.get("guest_pair_first_last", {}).get("S", "")

    contact_name_1 = WEDDING_DETAILS["contact_name_1"]
    contact_name_2 = WEDDING_DETAILS["contact_name_2"]
    contact_email_1 = WEDDING_DETAILS["contact_email_1"]
    contact_email_2 = WEDDING_DETAILS["contact_email_2"]

    pass_data = {
        "formatVersion": 1,
        "passTypeIdentifier": PASS_TYPE_ID,
        "serialNumber": hashlib.sha256(first_last.encode()).hexdigest()[:16],
        "teamIdentifier": TEAM_IDENTIFIER,
        "organizationName": f"{contact_name_1} & {contact_name_2}",
        "description": f"Wedding Invitation for {contact_name_1} & {contact_name_2}",
        "logoText": f"{contact_name_1} & {contact_name_2}",
        "foregroundColor": "rgb(255, 255, 255)",
        "backgroundColor": "rgb(60, 65, 76)",
        "labelColor": "rgb(255, 255, 255)",
        "eventTicket": {
            "primaryFields": [
                {"key": "guest", "label": "GUEST", "value": f"{first_name} {last_name}"}
            ],
            "secondaryFields": [
                {
                    "key": "event",
                    "label": "EVENT",
                    "value": f"The Wedding of {contact_name_1} & {contact_name_2}",
                }
            ],
            "auxiliaryFields": [
                {
                    "key": "date",
                    "label": "DATE",
                    "value": WEDDING_DETAILS["date"],
                    "textAlignment": "PKTextAlignmentLeft",
                },
                {
                    "key": "time",
                    "label": "TIME",
                    "value": WEDDING_DETAILS["time"],
                    "textAlignment": "PKTextAlignmentRight",
                },
            ],
            "backFields": [],
        },
    }

    if table_number:
        pass_data["eventTicket"]["backFields"].append(
            {"key": "table", "label": "TABLE", "value": str(table_number)}
        )

    pass_data["eventTicket"]["backFields"].extend([
        {"key": "venue", "label": "VENUE", "value": WEDDING_DETAILS["venue_name"]},
        {"key": "address", "label": "ADDRESS", "value": WEDDING_DETAILS["venue_address"]},
        {"key": "website", "label": "WEBSITE", "value": WEDDING_DETAILS["website_url"]},
    ])

    if has_plus_one and guest_pair:
        guest_first = guest_pair.split("_")[0].capitalize()
        guest_last = guest_pair.split("_")[1].capitalize()
        pass_data["eventTicket"]["backFields"].insert(
            0,
            {
                "key": "plus_one",
                "label": "PLUS ONE",
                "value": f"{guest_first} {guest_last}",
            },
        )

    log.info(f"Generated pass for {first_last}")
    return json.dumps(pass_data, indent=2).encode("utf-8")


@app.post("/wallet/pass/generate")
def generate_pass():
    """
    Generate an Apple Wallet pass for a user.

    Request body:
    {
        "first_last": "john_doe"
    }

    Returns base64-encoded .pkpass file.
    """
    auth_error = validate_internal_route(app.current_event)
    if auth_error:
        return auth_error

    try:
        payload = app.current_event.json_body
        first_last = payload.get("first_last")
        table_number = payload.get("table_number")

        if not first_last:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "Missing first_last field"},
            )

        user_data = get_user_from_db(first_last)
        if not user_data:
            return Response(
                status_code=404,
                content_type="application/json",
                body={"message": f"User {first_last} not found"},
            )

        pass_bytes = create_pass_for_user(user_data, table_number)
        pass_base64 = base64.b64encode(pass_bytes).decode("utf-8")

        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "Pass generated successfully",
                "first_last": first_last,
                "pass_data": pass_base64,
            },
        )

    except ValueError as e:
        log.warning(str(e))
        return Response(
            status_code=400,
            content_type="application/json",
            body={"message": str(e)},
        )
    except Exception as e:
        log.exception("Failed to generate pass")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to generate pass", "error": str(e)},
        )


@app.get("/wallet/ping")
def ping():
    """Health check endpoint"""
    return Response(
        status_code=200,
        content_type="application/json",
        body={"message": "wallet service is alive"},
    )


@app.get("/*")
@app.post("/*")
def not_found():
    log.info(f"route not found route={app.current_event.path}")
    return Response(
        status_code=404,
        content_type="application/json",
        body={"message": "Route not found"},
    )


@log.inject_lambda_context(log_event=True)
def handler(event, context):
    """Lambda handler"""
    try:
        return app.resolve(event, context)
    except Exception as e:
        log.exception("unhandled server error encountered")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Unhandled server error encountered"}),
        }
