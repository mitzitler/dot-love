import hmac
import io
import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from typing import Optional

import boto3
from boto3.dynamodb.types import TypeDeserializer

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.event_handler.api_gateway import APIGatewayHttpResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator

from openpyxl import Workbook
from openpyxl.styles import Font

# Environment Variables
USER_TABLE_NAME = os.environ["user_table_name"]
REGISTRY_ITEM_TABLE_NAME = os.environ["registry_item_table_name"]
REGISTRY_CLAIM_TABLE_NAME = os.environ["registry_claim_table_name"]
EXPORT_BUCKET_NAME = os.environ["export_bucket_name"]
INTERNAL_API_KEY = os.environ.get("internal_api_key", "")

INTERNAL_ROUTE_LIST = ["ping", "export"]

EXPORT_KEY_PREFIX = "thank-you-cards"
PRESIGNED_URL_EXPIRY_SECONDS = 3600
XLSX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
SHEET_TITLE = "Thank You Cards"
SHEET_HEADERS = (
    "Guest",
    "Partner",
    "Gift",
    "Brand",
    "Price",
    "Phone",
    "Street",
    "Line 2",
    "City",
    "State",
    "Zip",
    "Country",
)

# Powertools logger
log = Logger(service="miatun")

# Powertools routing
app = APIGatewayHttpResolver()


########################################################
# Dynamo Client (read-only subset of CWDynamoClient)
########################################################
class DynamoReadClient:
    """Read-only DynamoDB client: the subset of the shared CWDynamoClient
    that miatun needs (scan-all and batch-get), with pagination handled."""

    client = boto3.client("dynamodb")

    def get_all(
        self,
        table_name: str,
        filter_expression: Optional[str] = None,
        expression_attribute_values: Optional[dict] = None,
    ) -> list:
        """
        Get all items from a DynamoDB table with automatic pagination.
        Optionally filter results using a filter expression.

        :param table_name: Name of the DynamoDB table
        :param filter_expression: Optional filter expression
        :param expression_attribute_values: Values for the filter expression
        :return: List of all matching items (raw DynamoDB-typed maps)
        """
        scan_kwargs = {"TableName": table_name}

        if filter_expression:
            scan_kwargs["FilterExpression"] = filter_expression
            if expression_attribute_values:
                scan_kwargs["ExpressionAttributeValues"] = expression_attribute_values

        items = []
        last_evaluated_key = None

        while True:
            if last_evaluated_key:
                scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

            response = self.client.scan(**scan_kwargs)
            items.extend(response.get("Items", []))

            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

        log.info(f"Retrieved {len(items)} total items from {table_name}")
        return items

    def batch_get_items(
        self,
        table_name: str,
        keys: list,
        projection_expression: Optional[str] = None,
    ) -> list:
        """
        Get multiple items from a DynamoDB table in a batch operation with
        automatic handling of DynamoDB's batch size limit (100 items) and
        exponential-backoff retries for unprocessed keys.

        :param table_name: Name of the DynamoDB table
        :param keys: List of key dictionaries to get
        :param projection_expression: Optional projection expression
        :return: List of all matching items (raw DynamoDB-typed maps)
        """
        MAX_BATCH_SIZE = 100

        all_items = []

        for i in range(0, len(keys), MAX_BATCH_SIZE):
            batch_keys = keys[i : i + MAX_BATCH_SIZE]

            request_items = {table_name: {"Keys": batch_keys}}
            if projection_expression:
                request_items[table_name][
                    "ProjectionExpression"
                ] = projection_expression

            response = self.client.batch_get_item(RequestItems=request_items)

            if table_name in response.get("Responses", {}):
                all_items.extend(response["Responses"][table_name])

            # Retry unprocessed keys with exponential backoff
            unprocessed_keys = response.get("UnprocessedKeys", {})
            retry_count = 0
            max_retries = 5
            base_delay = 0.05  # 50 milliseconds

            while (
                unprocessed_keys
                and table_name in unprocessed_keys
                and retry_count < max_retries
            ):
                time.sleep(base_delay * (2**retry_count))

                retry_response = self.client.batch_get_item(
                    RequestItems=unprocessed_keys
                )

                if table_name in retry_response.get("Responses", {}):
                    all_items.extend(retry_response["Responses"][table_name])

                unprocessed_keys = retry_response.get("UnprocessedKeys", {})
                retry_count += 1

            if unprocessed_keys and table_name in unprocessed_keys:
                log.warning(
                    f"Failed to process all keys after {max_retries} retries. "
                    f"Remaining unprocessed keys: {len(unprocessed_keys[table_name]['Keys'])}"
                )

        return all_items


########################################################
# Export Data Model & Helpers
########################################################
@dataclass
class ThankYouRow:
    """One row of the thank-you-card spreadsheet: a delivered gift and the
    contact details of the guest who gave it."""

    guest: str
    partner: str
    gift: str
    brand: str
    price: str
    phone: str
    street: str
    second_line: str
    city: str
    state_loc: str
    zipcode: str
    country: str

    def as_tuple(self) -> tuple:
        return (
            self.guest,
            self.partner,
            self.gift,
            self.brand,
            self.price,
            self.phone,
            self.street,
            self.second_line,
            self.city,
            self.state_loc,
            self.zipcode,
            self.country,
        )


def title_case_first_last(first_last: str) -> str:
    """Format a first_last id ("john_smith") as a display name ("John Smith").

    Tolerant of empty strings and ids without an underscore.
    """
    if not first_last:
        return ""
    return " ".join(part.capitalize() for part in first_last.split("_") if part)


def format_price_cents(price_cents) -> str:
    """Format an integer cent amount as a dollar string, blank if unknown."""
    if price_cents is None:
        return ""
    try:
        return f"${int(price_cents) / 100:,.2f}"
    except (TypeError, ValueError):
        return ""


def fetch_export_data(dynamo_client: DynamoReadClient) -> tuple:
    """
    Fetch everything needed for the export:
    - all registry items marked received (delivered to us)
    - all registry claims
    - the user record for every distinct claimant

    :return: (received_items_by_id, claims, users_by_first_last) where items
             and users are deserialized dicts and claims are deserialized dicts
    """
    deserializer = TypeDeserializer()

    def deserialize(db_item: dict) -> dict:
        return {k: deserializer.deserialize(v) for k, v in db_item.items()}

    db_items = dynamo_client.get_all(
        REGISTRY_ITEM_TABLE_NAME,
        filter_expression="received = :received",
        expression_attribute_values={":received": {"BOOL": True}},
    )
    received_items_by_id = {}
    for db_item in db_items:
        item = deserialize(db_item)
        received_items_by_id[item.get("id")] = item

    db_claims = dynamo_client.get_all(REGISTRY_CLAIM_TABLE_NAME)
    claims = [deserialize(db_claim) for db_claim in db_claims]

    claimant_ids = sorted(
        {
            claim.get("claimant_id")
            for claim in claims
            if claim.get("claimant_id") and claim.get("item_id") in received_items_by_id
        }
        | {
            item.get("claimant_id")
            for item in received_items_by_id.values()
            if item.get("claimant_id")
        }
    )
    users_by_first_last = {}
    if claimant_ids:
        db_users = dynamo_client.batch_get_items(
            USER_TABLE_NAME,
            keys=[{"first_last": {"S": claimant_id}} for claimant_id in claimant_ids],
        )
        for db_user in db_users:
            user = deserialize(db_user)
            users_by_first_last[user.get("first_last")] = user

    return received_items_by_id, claims, users_by_first_last


def build_thank_you_rows(
    received_items_by_id: dict, claims: list, users_by_first_last: dict
) -> list:
    """
    Join received items with their claims and claimant user records into
    spreadsheet rows: one row per delivered gift.

    - Claims in UNCLAIMED state are ignored.
    - Duplicate (item, claimant) claims are collapsed to one row.
    - A received item with no claim row falls back to the item's own
      claimant_id (or blank) so no delivered gift is silently dropped.
    - Claimants missing from the users table (e.g. "plus_one") still get a
      row, with whatever contact fields are available left blank.
    """

    def build_row(item: dict, claimant_id: str) -> ThankYouRow:
        user = users_by_first_last.get(claimant_id, {})
        return ThankYouRow(
            guest=title_case_first_last(claimant_id),
            partner=title_case_first_last(user.get("guest_pair_first_last", "")),
            gift=item.get("item_name", ""),
            brand=item.get("brand", ""),
            price=format_price_cents(item.get("price_cents")),
            phone=user.get("phone", ""),
            street=user.get("street", ""),
            second_line=user.get("second_line", ""),
            city=user.get("city", ""),
            state_loc=user.get("state_loc", ""),
            zipcode=user.get("zipcode", ""),
            country=user.get("country", ""),
        )

    rows = []
    seen = set()
    items_with_claims = set()

    for claim in claims:
        item_id = claim.get("item_id")
        claimant_id = claim.get("claimant_id", "")
        if item_id not in received_items_by_id:
            continue
        if claim.get("claim_state") == "UNCLAIMED":
            continue
        if (item_id, claimant_id) in seen:
            continue
        seen.add((item_id, claimant_id))
        items_with_claims.add(item_id)
        rows.append(build_row(received_items_by_id[item_id], claimant_id))

    # Received items with no claim row at all
    for item_id, item in received_items_by_id.items():
        if item_id in items_with_claims:
            continue
        rows.append(build_row(item, item.get("claimant_id") or ""))

    rows.sort(key=lambda row: (row.guest, row.gift))
    return rows


def build_xlsx(rows: list) -> bytes:
    """Render thank-you rows as an xlsx workbook and return its bytes."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = SHEET_TITLE

    sheet.append(SHEET_HEADERS)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    sheet.freeze_panes = "A2"

    for row in rows:
        sheet.append(row.as_tuple())

    # Width tuned per column: names/gifts/addresses need more room
    column_widths = (22, 22, 40, 18, 10, 16, 28, 14, 18, 10, 10, 14)
    for column_cells, width in zip(sheet.columns, column_widths):
        sheet.column_dimensions[column_cells[0].column_letter].width = width

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def upload_export_to_s3(s3_client, xlsx_bytes: bytes) -> tuple:
    """Upload the workbook to the export bucket and presign a download URL.

    NOTE: the presigned URL is signed with this lambda's temporary role
    credentials, so it can expire before PRESIGNED_URL_EXPIRY_SECONDS if those
    credentials rotate. Fine for the download-immediately admin flow.

    :return: (object_key, presigned_url)
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    object_key = f"{EXPORT_KEY_PREFIX}/{EXPORT_KEY_PREFIX}-{timestamp}.xlsx"

    s3_client.put_object(
        Bucket=EXPORT_BUCKET_NAME,
        Key=object_key,
        Body=xlsx_bytes,
        ContentType=XLSX_CONTENT_TYPE,
    )

    presigned_url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": EXPORT_BUCKET_NAME, "Key": object_key},
        ExpiresIn=PRESIGNED_URL_EXPIRY_SECONDS,
    )

    return object_key, presigned_url


########################################################
# Controller Action Handler
########################################################
def validate_internal_route(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        event = app.current_event
        api_key = event.headers.get("Internal-Api-Key")
        if not api_key:
            api_key = event.headers.get("internal-api-key")

        if not api_key or not hmac.compare_digest(api_key, INTERNAL_API_KEY):
            return Response(
                status_code=401,
                content_type="application/json",
                body={"message": "no valid api key"},
            )

        return func(*args, **kwargs)

    return wrapper


@app.get("/miatun/ping")
def ping():
    return Response(
        status_code=200,
        content_type="application/json",
        body={"message": "ping success"},
    )


@app.post("/miatun/export")
@validate_internal_route
def export_thank_you_cards():
    """Generate the thank-you-card xlsx, upload it to S3, and return a
    presigned download URL."""
    try:
        received_items_by_id, claims, users_by_first_last = fetch_export_data(
            DYNAMO_CLIENT
        )
        rows = build_thank_you_rows(
            received_items_by_id, claims, users_by_first_last
        )
        xlsx_bytes = build_xlsx(rows)
        object_key, download_url = upload_export_to_s3(S3_CLIENT, xlsx_bytes)

        log.info(
            f"thank-you-card export complete rows={len(rows)} key={object_key}"
        )
        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "export success",
                "download_url": download_url,
                "row_count": len(rows),
                "expires_in_seconds": PRESIGNED_URL_EXPIRY_SECONDS,
            },
        )
    except Exception as e:
        log.exception("failed to generate thank-you-card export")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to generate export", "error": str(e)},
        )


# Fallback for unhandled routes
@app.get("/*")
@app.post("/*")
@app.patch("/*")
def not_found():
    log.info(f"route not found route={app.current_event.path}")
    return Response(
        status_code=404,
        content_type="application/json",
        body={"message": "Route not found"},
    )


@lambda_handler_decorator
def middleware_before(handler, event, context):
    # Exclude middleware for healthcheck and internal (api-key gated) routes
    if event["rawPath"].split("/")[-1] in INTERNAL_ROUTE_LIST:
        return handler(event, context)

    # append trace information
    trace_id = str(uuid.uuid4())
    amzn_trace_id = event["headers"].get("x-amzn-trace-id", "N/A")
    log.append_keys(
        trace_id=trace_id,
        amzn_trace_id=amzn_trace_id,
    )
    app.append_context(
        trace_id=trace_id,
        amzn_trace_id=amzn_trace_id,
    )

    # validate headers
    first_last = event["headers"].get("x-first-last")
    if not first_last:
        log.error("First and last name not included in headers")
        return {
            "code": 400,
            "message": "First and last name not included in headers",
        }
    log.append_keys(first_last=first_last)

    return handler(event, context)


# NOTE: log_event stays False so request headers (incl. Internal-Api-Key) don't
# land in CloudWatch
@log.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_HTTP, log_event=False
)
@middleware_before
def handler(event, context):
    try:
        return app.resolve(event, context)
    except Exception:
        log.exception("unhandled server error encountered")
        return {
            "code": 500,
            "message": "Unhandled server error encountered",
        }


# NOTE: Doing this at the top level so the client connections are preserved b/t lambda calls
# Initialize clients
DYNAMO_CLIENT = DynamoReadClient()
S3_CLIENT = boto3.client("s3")
