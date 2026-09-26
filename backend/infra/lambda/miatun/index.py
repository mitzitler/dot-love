import hmac
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime
from enum import Enum
from functools import wraps

import boto3
from boto3.dynamodb.types import TypeDeserializer

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.event_handler.api_gateway import APIGatewayHttpResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator

# Environment Variables
USER_TABLE_NAME = os.environ["user_table_name"]
REGISTRY_ITEM_TABLE_NAME = os.environ["registry_item_table_name"]
REGISTRY_CLAIM_TABLE_NAME = os.environ["registry_claim_table_name"]
LETTERS_TABLE_NAME = os.environ["letters_table_name"]
LETTERS_DISJOINED_PAIRS_TABLE_NAME = os.environ["letters_disjoined_pairs_table_name"]
INTERNAL_API_KEY = os.environ.get("internal_api_key", "")

# Handwrytten (robot-handwritten card mailing) config. Read with .get() so the
# lambda (and its tests) still import without them; the send routes refuse
# to run if any are missing.
HANDWRYTTEN_API_KEY = os.environ.get("handwrytten_api_key", "")
HANDWRYTTEN_CARD_ID = os.environ.get("handwrytten_card_id", "")
HANDWRYTTEN_FONT_LABEL = os.environ.get("handwrytten_font_label", "")
# Fixed sign-off, sent as Handwrytten's separate "wishes" field (not part of
# letter_body, so it doesn't count against LETTER_BODY_MAX_CHARS)
HANDWRYTTEN_WISHES = os.environ.get("handwrytten_wishes", "")
# JSON: {"first_name","last_name","address1","address2","city","state","zip"}
HANDWRYTTEN_SENDER = os.environ.get("handwrytten_sender", "")
HANDWRYTTEN_BASE_URL = "https://api.handwrytten.com/v2/"

# Max chars of handwritten message (greeting + body). The envelope address
# and the wishes sign-off are separate fields and don't count. Individual
# card designs may allow fewer — /send checks the card's own capacity too.
LETTER_BODY_MAX_CHARS = 500

INTERNAL_ROUTE_LIST = ["ping", "sync", "letter", "disjoin", "send", "send-one"]

# Powertools logger
log = Logger(service="miatun")

# Powertools routing
app = APIGatewayHttpResolver()


########################################################
# CWDynamo Client
# (copied from spectaculo/index.py — see that file for the canonical
# version; each service keeps its own copy, this is an established repo
# convention rather than a shared layer)
########################################################
class CWDynamoClient:
    client = boto3.client("dynamodb")

    def update(
        self,
        table_name,
        key_expression,
        field_value_map,
        manual_expression_attribute_map=None,
    ):
        field_names = [*field_value_map.keys()] + (
            []
            if manual_expression_attribute_map is None
            else [*manual_expression_attribute_map.keys()]
        )

        update_expression = self.format_update_expression(field_names)

        # Alias every attribute name (e.g. #source -> "source") so field
        # names that happen to be DynamoDB reserved words (like "source")
        # don't break the UpdateExpression.
        expression_attribute_names = {f"#{name}": name for name in field_names}

        expression_attribute_values = self.format_update_expression_attribute_values(
            field_value_map, manual_expression_attribute_map, operation="update"
        )

        res = self.client.update_item(
            TableName=table_name,
            Key=key_expression,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",
        )

        return res

    def get(self, table_name, key_expression):
        return self.client.get_item(TableName=table_name, Key=key_expression).get(
            "Item", None
        )

    def get_all(
        self, table_name, filter_expression=None, expression_attribute_values=None
    ):
        """
        Get all items from a DynamoDB table with automatic pagination.
        Optionally filter results using a filter expression.

        :param table_name: Name of the DynamoDB table
        :param filter_expression: Optional filter expression
        :param expression_attribute_values: Values for the filter expression
        :return: List of all matching items
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

            if len(items) > 1000:
                log.info(
                    f"Continuing pagination for table {table_name}, retrieved {len(items)} items so far"
                )

        log.info(f"Retrieved {len(items)} total items from {table_name}")
        return items

    def get_all_of_col(self, table_name, col_name):
        """
        Get specific column values for all items in a table with automatic pagination.

        :param table_name: Name of the DynamoDB table
        :param col_name: Column/attribute name to retrieve
        :return: List of deserialized values for the specified column
        """
        deserializer = TypeDeserializer()

        projection_items = []
        last_evaluated_key = None

        while True:
            scan_kwargs = {"TableName": table_name, "ProjectionExpression": col_name}

            if last_evaluated_key:
                scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

            response = self.client.scan(**scan_kwargs)

            items = response.get("Items", [])
            for item in items:
                deserialized_item = {
                    k: deserializer.deserialize(v) for k, v in item.items()
                }
                projection_items.append(deserialized_item)

            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

            if len(projection_items) > 1000:
                log.info(
                    f"Continuing pagination for column {col_name} in table {table_name}, retrieved {len(projection_items)} items so far"
                )

        log.info(
            f"Retrieved {len(projection_items)} values for column {col_name} from {table_name}"
        )
        return projection_items

    def query(
        self,
        table_name,
        key_condition_expression,
        expression_attribute_values,
        index_name=None,
    ):
        """
        Query a DynamoDB table or index with automatic pagination.

        :param table_name: Name of the DynamoDB table
        :param key_condition_expression: Key condition expression for the query
        :param expression_attribute_values: Values for the key condition expression
        :param index_name: Optional index name to query
        :return: List of all matching items
        """
        query_kwargs = {
            "TableName": table_name,
            "KeyConditionExpression": key_condition_expression,
            "ExpressionAttributeValues": expression_attribute_values,
        }

        if index_name:
            query_kwargs["IndexName"] = index_name

        items = []
        last_evaluated_key = None

        while True:
            if last_evaluated_key:
                query_kwargs["ExclusiveStartKey"] = last_evaluated_key

            response = self.client.query(**query_kwargs)

            items.extend(response.get("Items", []))

            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

            if len(items) > 1000:
                log.info(
                    f"Continuing pagination for query on {table_name}, retrieved {len(items)} items so far"
                )

        log.info(f"Retrieved {len(items)} total items from query on {table_name}")
        return items

    def create(
        self,
        table_name,
        key_expression,
        field_value_map,
        manual_expression_attribute_map=None,
    ):
        item = key_expression
        for field_name, field_value in field_value_map.items():
            dynamo_formatted_value_mapping = self.dynamo_format_value_mapping(
                field_name, field_value, operation="create"
            )
            item.update(dynamo_formatted_value_mapping)
        if manual_expression_attribute_map is not None:
            item.update(manual_expression_attribute_map)

        res = self.client.put_item(TableName=table_name, Item=item)

        return res

    def delete(self, table_name, key_expression):
        return self.client.delete_item(TableName=table_name, Key=key_expression)

    def batch_get_items(self, table_name, keys, projection_expression=None):
        """
        Get multiple items from a DynamoDB table in a batch operation with automatic handling
        of DynamoDB's batch size limit (100 items).

        :param table_name: Name of the DynamoDB table
        :param keys: List of key dictionaries to get
        :param projection_expression: Optional projection expression to limit attributes returned
        :return: List of all matching items
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

            unprocessed_keys = response.get("UnprocessedKeys", {})
            retry_count = 0
            max_retries = 5
            base_delay = 0.05  # 50 milliseconds

            while (
                unprocessed_keys
                and table_name in unprocessed_keys
                and retry_count < max_retries
            ):
                delay = base_delay * (2**retry_count)
                time.sleep(delay)

                retry_response = self.client.batch_get_item(
                    RequestItems=unprocessed_keys
                )

                if table_name in retry_response.get("Responses", {}):
                    all_items.extend(retry_response["Responses"][table_name])

                unprocessed_keys = retry_response.get("UnprocessedKeys", {})
                retry_count += 1

            if unprocessed_keys and table_name in unprocessed_keys:
                log.warning(
                    f"Failed to process all keys after {max_retries} retries. Remaining unprocessed keys: {len(unprocessed_keys[table_name]['Keys'])}"
                )

        return all_items

    def format_update_expression_attribute_values(
        self, field_value_map, manual_expression_attribute_map, operation
    ):
        expression_attribute_values = {}
        for field_name, field_value in field_value_map.items():
            dynamo_formatted_value_mapping = self.dynamo_format_value_mapping(
                field_name, field_value, operation=operation
            )
            expression_attribute_values.update(dynamo_formatted_value_mapping)
        if manual_expression_attribute_map is not None:
            if operation == "update":
                semicolon_manual_expr_attr_map = {}
                for key, value in manual_expression_attribute_map.items():
                    new_key = ":" + key
                    semicolon_manual_expr_attr_map.update({new_key: value})

                expression_attribute_values.update(semicolon_manual_expr_attr_map)
            else:
                expression_attribute_values.update(manual_expression_attribute_map)
        return expression_attribute_values

    def dynamo_format_value_mapping(self, field_name, field_value, operation):
        """
        Format a value for DynamoDB, handling all data types appropriately.

        :param field_name: The field name
        :param field_value: The value to format
        :param operation: The operation type ('update' or 'create')
        :return: Formatted value mapping for DynamoDB
        """
        if operation == "update":
            field_name = ":" + field_name

        dynamoType = self.determine_dynamo_data_type(field_value)

        if dynamoType == "N" and (
            isinstance(field_value, int) or isinstance(field_value, float)
        ):
            dynamoValue = str(field_value)
        elif dynamoType == "BOOL" and isinstance(field_value, str):
            dynamoValue = field_value == "True"
        elif dynamoType == "NULL":
            dynamoValue = True
        elif dynamoType == "M" and isinstance(field_value, dict):
            dynamoValue = self._format_map_for_dynamo(field_value)
        elif dynamoType == "L" and isinstance(field_value, list):
            dynamoValue = self._format_list_for_dynamo(field_value)
        elif dynamoType in ("SS", "NS") and isinstance(field_value, list):
            if dynamoType == "NS":
                dynamoValue = [str(x) for x in field_value]
            else:
                dynamoValue = field_value
        else:
            dynamoValue = field_value

        return {field_name: {dynamoType: dynamoValue}}

    def _format_map_for_dynamo(self, map_value):
        """
        Format a map (dict) for DynamoDB by recursively formatting each value.

        :param map_value: Dictionary to format
        :return: Formatted map for DynamoDB
        """
        formatted_map = {}
        for k, v in map_value.items():
            dynamo_type = self.determine_dynamo_data_type(v)

            if dynamo_type == "N" and (isinstance(v, int) or isinstance(v, float)):
                formatted_map[k] = {"N": str(v)}
            elif dynamo_type == "BOOL":
                formatted_map[k] = {"BOOL": v if isinstance(v, bool) else v == "True"}
            elif dynamo_type == "NULL":
                formatted_map[k] = {"NULL": True}
            elif dynamo_type == "M" and isinstance(v, dict):
                formatted_map[k] = {"M": self._format_map_for_dynamo(v)}
            elif dynamo_type == "L" and isinstance(v, list):
                formatted_map[k] = {"L": self._format_list_for_dynamo(v)}
            elif dynamo_type in ("SS", "NS") and isinstance(v, list):
                if dynamo_type == "NS":
                    formatted_map[k] = {"NS": [str(x) for x in v]}
                else:
                    formatted_map[k] = {"SS": v}
            else:
                formatted_map[k] = {dynamo_type: v}

        return formatted_map

    def _format_list_for_dynamo(self, list_value):
        """
        Format a list for DynamoDB by recursively formatting each value.

        :param list_value: List to format
        :return: Formatted list for DynamoDB
        """
        formatted_list = []
        for item in list_value:
            dynamo_type = self.determine_dynamo_data_type(item)

            if dynamo_type == "N" and (
                isinstance(item, int) or isinstance(item, float)
            ):
                formatted_list.append({"N": str(item)})
            elif dynamo_type == "BOOL":
                formatted_list.append(
                    {"BOOL": item if isinstance(item, bool) else item == "True"}
                )
            elif dynamo_type == "NULL":
                formatted_list.append({"NULL": True})
            elif dynamo_type == "M" and isinstance(item, dict):
                formatted_list.append({"M": self._format_map_for_dynamo(item)})
            elif dynamo_type == "L" and isinstance(item, list):
                formatted_list.append({"L": self._format_list_for_dynamo(item)})
            else:
                formatted_list.append({dynamo_type: item})

        return formatted_list

    def determine_dynamo_data_type(self, value):
        """
        Determine the DynamoDB data type for a given Python value.

        :param value: Python value to analyze
        :return: DynamoDB data type string
        """
        if value is None:
            return "NULL"
        elif isinstance(value, str):
            return "S"
        elif isinstance(value, bool):
            return "BOOL"
        elif isinstance(value, int) or isinstance(value, float):
            return "N"
        elif isinstance(value, dict):
            return "M"
        elif isinstance(value, list):
            if not value:
                return "L"
            if all(isinstance(x, str) for x in value):
                return "SS"
            elif all(isinstance(x, (int, float)) for x in value):
                return "NS"
            else:
                return "L"

        raise Exception(
            f"CWDynamo Client Error: Unhandled data type provided for value: {value}"
        )

    def format_update_expression(self, field_name_list):
        if not field_name_list:
            raise ValueError("No fields provided for update expression")

        update_expression = f"SET #{field_name_list[0]} = :{field_name_list[0]}"
        remaining_fields = field_name_list[1:]

        for field_name in remaining_fields:
            update_expression = update_expression + f", #{field_name} = :{field_name}"

        return update_expression


########################################################
# Letters Data Model
########################################################
class LetterStatus(Enum):
    DRAFT = 1
    WRITTEN = 2
    READY_TO_SEND = 3
    SENT = 4

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"LetterStatus.{self.name}"


class LetterRecord:
    def __init__(
        self,
        id,
        guest="",
        partner="",
        claimant_id="",
        gifts=None,
        phone="",
        street="",
        second_line="",
        city="",
        state_loc="",
        zipcode="",
        country="",
        letter_body="",
        status=None,
        source="MANUAL",
        updated_at=None,
        handwrytten_order_id="",
        sent_at="",
    ):
        """
        A thank-you letter for a household (a solo guest, or a guest+partner
        couple): contact info plus every gift they received, plus the
        letter body text and its writing/send status. One letter covers
        every gift the household received, so a couple who each claimed a
        gift — or a guest who received several — gets a single letter
        instead of one per gift.

        :param id (STR): a deterministic key derived from the household
            (see build_letter_records), so re-syncing upserts in place
            instead of duplicating.
        :param gifts (list[dict]): each dict has "gift", "brand",
            "price_cents".
        :param status (LetterStatus): DRAFT/WRITTEN/READY_TO_SEND/SENT.
        :param source (STR): "SYNC" (populated by the claims sync) or
            "MANUAL" (hand-entered by an admin).
        :param handwrytten_order_id (STR): set when mailed via
            Handwrytten (see POST /miatun/send).
        :param sent_at (STR): ISO timestamp of the Handwrytten send.
        """
        self.id = id
        self.guest = guest
        self.partner = partner
        self.claimant_id = claimant_id
        self.gifts = gifts if gifts is not None else []
        self.phone = phone
        self.street = street
        self.second_line = second_line
        self.city = city
        self.state_loc = state_loc
        self.zipcode = zipcode
        self.country = country
        self.letter_body = letter_body
        self.status = status or LetterStatus.DRAFT
        self.source = source
        self.updated_at = updated_at or datetime.now().isoformat()
        self.handwrytten_order_id = handwrytten_order_id
        self.sent_at = sent_at

    def as_map(self):
        return {
            "id": self.id,
            "guest": self.guest,
            "partner": self.partner,
            "claimant_id": self.claimant_id,
            "gifts": self.gifts,
            "phone": self.phone,
            "street": self.street,
            "second_line": self.second_line,
            "city": self.city,
            "state_loc": self.state_loc,
            "zipcode": self.zipcode,
            "country": self.country,
            "letter_body": self.letter_body,
            "status": self.status.name if self.status else LetterStatus.DRAFT.name,
            "source": self.source,
            "updated_at": self.updated_at,
            "handwrytten_order_id": self.handwrytten_order_id,
            "sent_at": self.sent_at,
        }

    def __str__(self):
        return (
            f"LetterRecord(id={self.id}, guest={self.guest}, "
            f"gifts={len(self.gifts)}, status={self.status})"
        )

    def __repr__(self):
        return (
            f"LetterRecord(id={self.id!r}, guest={self.guest!r}, "
            f"gifts={self.gifts!r}, status={self.status!r})"
        )

    @staticmethod
    def from_db(letter_data):
        """
        Create a LetterRecord object from DynamoDB data. Missing
        `letter_body`/`status` (e.g. a row that's only ever been synced, never
        opened in the editor) default to "" / DRAFT.
        """
        if not letter_data:
            return None

        deserializer = TypeDeserializer()
        letter = {k: deserializer.deserialize(v) for k, v in letter_data.items()}

        status_str = letter.get("status") or LetterStatus.DRAFT.name
        try:
            status = LetterStatus[status_str]
        except KeyError:
            status = LetterStatus.DRAFT

        gifts = []
        for raw_gift in letter.get("gifts") or []:
            gift_price_cents = raw_gift.get("price_cents")
            gifts.append(
                {
                    "gift": raw_gift.get("gift", ""),
                    "brand": raw_gift.get("brand", ""),
                    "price_cents": (
                        int(gift_price_cents) if gift_price_cents is not None else None
                    ),
                }
            )

        try:
            return LetterRecord(
                id=letter.get("id"),
                guest=letter.get("guest", ""),
                partner=letter.get("partner", ""),
                claimant_id=letter.get("claimant_id", ""),
                gifts=gifts,
                phone=letter.get("phone", ""),
                street=letter.get("street", ""),
                second_line=letter.get("second_line", ""),
                city=letter.get("city", ""),
                state_loc=letter.get("state_loc", ""),
                zipcode=letter.get("zipcode", ""),
                country=letter.get("country", ""),
                letter_body=letter.get("letter_body", ""),
                status=status,
                source=letter.get("source", "MANUAL"),
                updated_at=letter.get("updated_at"),
                handwrytten_order_id=letter.get("handwrytten_order_id", ""),
                sent_at=letter.get("sent_at", ""),
            )
        except Exception as e:
            log.exception(f"Error creating LetterRecord from data: {e}")
            return None

    @staticmethod
    def from_letter_id_db(letter_id, dynamo_client):
        """
        Get a letter from the database by its ID.

        :param letter_id: The ID of the letter
        :param dynamo_client: The DynamoDB client
        :return: LetterRecord object or None if not found
        """
        try:
            key_expression = {"id": {"S": letter_id}}
            letter_data = dynamo_client.get(LETTERS_TABLE_NAME, key_expression)

            if not letter_data:
                log.info(f"No letter found with ID: {letter_id}")
                return None

            return LetterRecord.from_db(letter_data)
        except Exception as e:
            log.exception(f"Error retrieving letter with ID {letter_id}: {str(e)}")
            return None

    @staticmethod
    def get_all_letters_db(dynamo_client):
        """
        Get all letters from the database.

        :param dynamo_client: The DynamoDB client
        :return: List of LetterRecord objects
        """
        try:
            letters_data = dynamo_client.get_all(LETTERS_TABLE_NAME)

            letters = []
            for letter_data in letters_data:
                letter = LetterRecord.from_db(letter_data)
                if letter:
                    letters.append(letter)

            return letters
        except Exception as e:
            log.exception(f"Error retrieving all letters: {str(e)}")
            return []

    def update_db(self, dynamo_client):
        """
        Full write of every field, including letter_body/status/source.
        Used by manual create and by the admin edit (PATCH) route. Never
        call this from the claims-sync path — use sync_upsert_db instead, so
        a re-sync can't clobber an in-progress letter edit.
        """
        key_expression = {"id": {"S": self.id}}
        field_value_map = {
            "guest": self.guest,
            "partner": self.partner,
            "claimant_id": self.claimant_id,
            "gifts": self.gifts,
            "phone": self.phone,
            "street": self.street,
            "second_line": self.second_line,
            "city": self.city,
            "state_loc": self.state_loc,
            "zipcode": self.zipcode,
            "country": self.country,
            "letter_body": self.letter_body,
            "status": self.status.name if self.status else LetterStatus.DRAFT.name,
            "source": self.source,
            "handwrytten_order_id": self.handwrytten_order_id,
            "sent_at": self.sent_at,
            "updated_at": datetime.now().isoformat(),
        }

        res = dynamo_client.update(LETTERS_TABLE_NAME, key_expression, field_value_map)

        return res

    def sync_upsert_db(self, dynamo_client):
        """
        Upsert used by the claims sync: writes only contact/gift fields and
        never touches letter_body/status, so re-running sync can't overwrite
        a letter that's already been written.
        """
        key_expression = {"id": {"S": self.id}}
        field_value_map = {
            "guest": self.guest,
            "partner": self.partner,
            "claimant_id": self.claimant_id,
            "gifts": self.gifts,
            "phone": self.phone,
            "street": self.street,
            "second_line": self.second_line,
            "city": self.city,
            "state_loc": self.state_loc,
            "zipcode": self.zipcode,
            "country": self.country,
            "source": "SYNC",
            "updated_at": datetime.now().isoformat(),
        }

        res = dynamo_client.update(LETTERS_TABLE_NAME, key_expression, field_value_map)

        return res

    def delete_db(self, dynamo_client):
        """
        Delete this letter from the database.
        """
        key_expression = {"id": {"S": self.id}}
        return dynamo_client.delete(LETTERS_TABLE_NAME, key_expression)


def title_case_first_last(first_last: str) -> str:
    """Format a first_last id ("john_smith") as a display name ("John Smith").

    Tolerant of empty strings and ids without an underscore.
    """
    if not first_last:
        return ""
    return " ".join(part.capitalize() for part in first_last.split("_") if part)


def deserialize_item(db_item: dict) -> dict:
    """Deserialize a raw (typed) DynamoDB item into a plain dict."""
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in db_item.items()}


def disjoined_pair_key(id_a: str, id_b: str) -> str:
    """Canonical, order-independent key for a claimant pair, matching the
    "couple:a|b" household-key convention used by build_letter_records."""
    return "|".join(sorted([id_a, id_b]))


def get_user_db(dynamo_client, first_last: str) -> dict:
    """Look up a single user record by their first_last id."""
    raw = dynamo_client.get(USER_TABLE_NAME, {"first_last": {"S": first_last}})
    return deserialize_item(raw) if raw else {}


def save_disjoined_pair_db(dynamo_client, pair_key: str) -> None:
    """Record that this claimant pair should never be merged into one
    household letter, regardless of what guest_pair_first_last says."""
    dynamo_client.update(
        LETTERS_DISJOINED_PAIRS_TABLE_NAME,
        {"pair_key": {"S": pair_key}},
        {"disjoined_at": datetime.now().isoformat()},
    )


def fetch_sync_data(dynamo_client) -> tuple:
    """
    Fetch everything needed to sync letters from claims data:
    - all registry items marked received (delivered to us)
    - all registry claims
    - the user record for every distinct claimant
    - every claimant pair that's been disjoined (see POST /miatun/disjoin)

    :return: (received_items_by_id, claims, users_by_first_last,
             disjoined_pair_keys) where items and users are deserialized
             dicts, claims are deserialized dicts, and disjoined_pair_keys is
             a set of "sorted(id_a, id_b)"-joined-by-"|" strings.
    """
    db_items = dynamo_client.get_all(
        REGISTRY_ITEM_TABLE_NAME,
        filter_expression="received = :received",
        expression_attribute_values={":received": {"BOOL": True}},
    )
    received_items_by_id = {}
    for db_item in db_items:
        item = deserialize_item(db_item)
        received_items_by_id[item.get("id")] = item

    db_claims = dynamo_client.get_all(REGISTRY_CLAIM_TABLE_NAME)
    claims = [deserialize_item(db_claim) for db_claim in db_claims]

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
            user = deserialize_item(db_user)
            users_by_first_last[user.get("first_last")] = user

    db_disjoined = dynamo_client.get_all(LETTERS_DISJOINED_PAIRS_TABLE_NAME)
    disjoined_pair_keys = {
        deserialize_item(row)["pair_key"] for row in db_disjoined
    }

    return received_items_by_id, claims, users_by_first_last, disjoined_pair_keys


def build_letter_records(
    received_items_by_id: dict,
    claims: list,
    users_by_first_last: dict,
    disjoined_pair_keys: set = None,
) -> list:
    """
    Join received items with their claims and claimant user records into
    LetterRecords, one per household — a solo guest, or a guest+partner
    couple — so a couple who each claimed a separate gift, or a guest who
    received several gifts, gets a single letter listing every gift
    instead of one letter per gift.

    - Claims in UNCLAIMED state are ignored.
    - Duplicate (item, claimant) claims are collapsed to one gift line.
    - A received item with no claim row falls back to the item's own
      claimant_id (or blank) so no delivered gift is silently dropped; a
      blank/unknown claimant still gets its own letter per item (there's
      no identity to group it by).
    - Household grouping: a claimant with a partner on file
      (`guest_pair_first_last`) is grouped with that partner under a
      canonical (order-independent) key, so it doesn't matter which of the
      two actually claimed a given gift. A claimant with no partner on
      file is grouped alone. A pair present in `disjoined_pair_keys` (see
      POST /miatun/disjoin) is always grouped separately instead, even
      though `guest_pair_first_last` still pairs them — that field also
      drives real RSVP date-pairing and is never mutated by this feature.
    - Letter id is a deterministic key derived from the household (or, for
      the no-identifiable-claimant fallback, the source item's id), so
      re-syncing upserts in place instead of duplicating.

    :param disjoined_pair_keys: optional set of "sorted(id_a, id_b)"-joined
        -by-"|" strings; defaults to no exceptions (every pair with
        guest_pair_first_last set is grouped as a couple).
    """
    disjoined = disjoined_pair_keys or set()

    def effective_partner_id(claimant_id: str) -> str:
        user = users_by_first_last.get(claimant_id, {})
        partner_id = user.get("guest_pair_first_last") or ""
        if not partner_id:
            return ""
        if disjoined_pair_key(claimant_id, partner_id) in disjoined:
            return ""
        return partner_id

    def gift_line(item: dict) -> dict:
        price_cents = item.get("price_cents")
        return {
            "gift": item.get("item_name", ""),
            "brand": item.get("brand", ""),
            "price_cents": int(price_cents) if price_cents is not None else None,
        }

    def household_key(claimant_id: str) -> str:
        partner_id = effective_partner_id(claimant_id)
        if partner_id:
            return "couple:" + "|".join(sorted([claimant_id, partner_id]))
        return "guest:" + claimant_id

    # Gather (item, claimant_id) pairs: one per delivered gift.
    gift_claims = []
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
        gift_claims.append((received_items_by_id[item_id], claimant_id))

    # Received items with no claim row at all
    for item_id, item in received_items_by_id.items():
        if item_id in items_with_claims:
            continue
        gift_claims.append((item, item.get("claimant_id") or ""))

    # Group gifts by household.
    households = {}
    for item, claimant_id in gift_claims:
        if claimant_id:
            key = household_key(claimant_id)
        else:
            # No identifiable claimant — nothing to group by, one letter
            # per orphan item (matches prior behavior for this edge case).
            key = f"item:{item.get('id')}"

        household = households.setdefault(key, {"claimant_ids": set(), "gifts": []})
        if claimant_id:
            household["claimant_ids"].add(claimant_id)
        household["gifts"].append(gift_line(item))

    letters = []
    for key, household in households.items():
        claimant_ids = sorted(household["claimant_ids"])
        primary_claimant_id = claimant_ids[0] if claimant_ids else ""
        user = users_by_first_last.get(primary_claimant_id, {})
        partner_id = effective_partner_id(primary_claimant_id) if primary_claimant_id else ""

        letters.append(
            LetterRecord(
                id=key,
                guest=title_case_first_last(primary_claimant_id),
                partner=title_case_first_last(partner_id),
                claimant_id=primary_claimant_id,
                gifts=household["gifts"],
                phone=user.get("phone", ""),
                street=user.get("street", ""),
                second_line=user.get("second_line", ""),
                city=user.get("city", ""),
                state_loc=user.get("state_loc", ""),
                zipcode=user.get("zipcode", ""),
                country=user.get("country", ""),
                source="SYNC",
            )
        )

    letters.sort(key=lambda letter: letter.guest)
    return letters


########################################################
# Handwrytten (robot-handwritten card mailing)
# API ref: https://www.handwrytten.com/api-redoc/ — request shapes mirror the
# official SDK (github.com/handwrytten/handwrytten-python-sdk); called with
# urllib so no new dependency lands in the layer.
########################################################
US_COUNTRY_ALIASES = {
    "",
    "US",
    "USA",
    "U.S.",
    "U.S.A.",
    "UNITED STATES",
    "UNITED STATES OF AMERICA",
}


class HandwryttenError(Exception):
    pass


class HandwryttenClient:
    def __init__(self, api_key, base_url=HANDWRYTTEN_BASE_URL, timeout=10):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

    def _request(self, method, path, params=None, body=None):
        """Make a single (never retried — a retried POST could double-order)
        request and return the parsed JSON body."""
        url = self.base_url + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                # Handwrytten takes the raw key, no "Bearer " prefix
                "Authorization": self.api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                raw = res.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")[:500]
            raise HandwryttenError(
                f"{method} {path} failed with HTTP {e.code}: {detail}"
            ) from e
        except urllib.error.URLError as e:
            raise HandwryttenError(f"{method} {path} failed: {e.reason}") from e

        parsed = json.loads(raw) if raw else {}
        # Some Handwrytten errors come back as HTTP 200 with status=error
        if isinstance(parsed, dict) and parsed.get("status") == "error":
            raise HandwryttenError(
                f"{method} {path} returned an error: {parsed.get('message') or parsed}"
            )
        return parsed

    def get_card(self, card_id):
        data = self._request("GET", "cards/view", params={"card_id": card_id})
        card = data.get("card") if isinstance(data, dict) else None
        if not isinstance(card, dict) or str(card.get("id")) != str(card_id):
            raise HandwryttenError(f"No Handwrytten card found with id {card_id}")
        return card

    def basket_count(self):
        data = self._request("GET", "basket/count")
        return int(data.get("count", 0)) if isinstance(data, dict) else 0

    def place_basket(self, card_id, font_label, addresses):
        """Add one order to the basket covering every address row. Each row
        carries its own to_*/from_* fields plus message/wishes."""
        return self._request(
            "POST",
            "orders/placeBasket",
            body={
                "card_id": int(card_id),
                "font": font_label,
                "addresses": addresses,
            },
        )

    def send_basket(self):
        """Check out everything in the basket as a single order."""
        return self._request("POST", "basket/send", body={})


def get_handwrytten_client():
    return HandwryttenClient(HANDWRYTTEN_API_KEY)


def missing_handwrytten_config() -> list:
    config = {
        "handwrytten_api_key": HANDWRYTTEN_API_KEY,
        "handwrytten_card_id": HANDWRYTTEN_CARD_ID,
        "handwrytten_font_label": HANDWRYTTEN_FONT_LABEL,
        "handwrytten_wishes": HANDWRYTTEN_WISHES,
        "handwrytten_sender": HANDWRYTTEN_SENDER,
    }
    return [name for name, value in config.items() if not value]


def sender_address_fields(sender_json: str) -> dict:
    """Parse the sender (return address) config into Handwrytten from_*
    fields. Raises ValueError if it isn't a JSON object."""
    sender = json.loads(sender_json)
    if not isinstance(sender, dict):
        raise ValueError("handwrytten_sender must be a JSON object")
    keys = ["first_name", "last_name", "address1", "address2", "city", "state", "zip"]
    return {f"from_{key}": sender[key] for key in keys if sender.get(key)}


def envelope_name(guest: str, partner: str) -> tuple:
    """Split a letter's display names into Handwrytten's first/last name
    fields so the envelope reads naturally (Handwrytten prints them as
    "first last"):
    - solo: "Jane Doe" -> ("Jane", "Doe")
    - couple sharing a last name: ("Jane & John", "Smith")
    - couple with different last names: ("Jane Doe &", "John Smith")
    """
    guest_parts = guest.split()
    partner_parts = partner.split()
    if not partner_parts:
        if len(guest_parts) < 2:
            return guest.strip(), ""
        return " ".join(guest_parts[:-1]), guest_parts[-1]
    if (
        len(guest_parts) >= 2
        and len(partner_parts) >= 2
        and guest_parts[-1].lower() == partner_parts[-1].lower()
    ):
        first = f"{' '.join(guest_parts[:-1])} & {' '.join(partner_parts[:-1])}"
        return first, guest_parts[-1]
    return f"{' '.join(guest_parts)} &", " ".join(partner_parts)


def letter_send_problems(letter, max_chars: int) -> list:
    """Everything that would stop this letter from being mailed."""
    problems = []
    body = letter.letter_body or ""
    if not body.strip():
        problems.append("letter body is empty")
    elif len(body) > max_chars:
        problems.append(
            f"letter body is {len(body)} characters; this card fits {max_chars}"
        )
    if not (letter.guest or "").strip():
        problems.append("no recipient name")
    for field, label in [
        ("street", "street"),
        ("city", "city"),
        ("state_loc", "state"),
        ("zipcode", "zip"),
    ]:
        if not (getattr(letter, field) or "").strip():
            problems.append(f"missing {label}")
    country = (letter.country or "").strip().upper()
    if country not in US_COUNTRY_ALIASES:
        problems.append(
            f"non-US country '{letter.country}' — send this one manually"
        )
    return problems


def recipient_row(letter, sender_fields: dict) -> dict:
    """One Handwrytten placeBasket address row for this letter. Country is
    omitted: Handwrytten defaults to US, and letter_send_problems() rejects
    anything else."""
    first_name, last_name = envelope_name(letter.guest or "", letter.partner or "")
    row = {
        "to_first_name": first_name,
        "to_last_name": last_name,
        "to_address1": letter.street.strip(),
        "to_city": letter.city.strip(),
        "to_state": letter.state_loc.strip(),
        "to_zip": letter.zipcode.strip(),
        "message": letter.letter_body,
        "wishes": HANDWRYTTEN_WISHES,
    }
    if (letter.second_line or "").strip():
        row["to_address2"] = letter.second_line.strip()
    row.update(sender_fields)
    return row


def json_response(status_code, body):
    return Response(status_code=status_code, content_type="application/json", body=body)


def send_letters_via_handwrytten(letters, dry_run, mark_sent, hw_client, dynamo_client):
    """
    Validate and (unless dry_run) mail `letters` through Handwrytten as a
    single basket checkout. Shared by POST /miatun/send and POST
    /miatun/send-one so a one-card test exercises the exact batch path.

    All-or-nothing: if any letter fails validation, nothing is sent. A dry
    run still looks up the card (read-only) to verify the API key/card id
    and learn the card's character capacity, but never touches the basket.
    """
    missing = missing_handwrytten_config()
    if missing:
        return json_response(
            500, {"message": f"Handwrytten config missing: {', '.join(missing)}"}
        )
    try:
        sender_fields = sender_address_fields(HANDWRYTTEN_SENDER)
    except (ValueError, TypeError) as e:
        return json_response(
            500, {"message": f"handwrytten_sender is not valid JSON: {e}"}
        )

    try:
        card = hw_client.get_card(HANDWRYTTEN_CARD_ID)
    except HandwryttenError as e:
        log.exception("Handwrytten card lookup failed")
        return json_response(
            502, {"message": "Could not look up the Handwrytten card", "error": str(e)}
        )

    max_chars = LETTER_BODY_MAX_CHARS
    try:
        card_chars = int(card.get("characters") or 0)
    except (TypeError, ValueError):
        card_chars = 0
    if card_chars > 0:
        max_chars = min(max_chars, card_chars)

    invalid = []
    for letter in letters:
        problems = letter_send_problems(letter, max_chars)
        if problems:
            invalid.append(
                {"letter_id": letter.id, "guest": letter.guest, "problems": problems}
            )
    if invalid:
        return json_response(
            400,
            {
                "message": f"{len(invalid)} letter(s) can't be sent; nothing was sent",
                "max_chars": max_chars,
                "invalid_letters": invalid,
            },
        )

    rows = [recipient_row(letter, sender_fields) for letter in letters]

    if dry_run:
        return json_response(
            200,
            {
                "message": "dry run; nothing was sent",
                "dry_run": True,
                "count": len(letters),
                "max_chars": max_chars,
                "card_id": HANDWRYTTEN_CARD_ID,
                "font": HANDWRYTTEN_FONT_LABEL,
                "recipients": [
                    {"letter_id": letter.id, **row} for letter, row in zip(letters, rows)
                ],
            },
        )

    # Refuse to check out a basket we didn't fill: leftovers from an earlier
    # failed attempt would otherwise get mailed alongside this batch.
    try:
        existing = hw_client.basket_count()
    except HandwryttenError as e:
        log.exception("Handwrytten basket count failed")
        return json_response(
            502, {"message": "Could not check the Handwrytten basket", "error": str(e)}
        )
    if existing:
        return json_response(
            409,
            {
                "message": f"The Handwrytten basket already has {existing} item(s). Review or clear it in the Handwrytten dashboard, then retry; nothing was sent."
            },
        )

    try:
        placed = hw_client.place_basket(HANDWRYTTEN_CARD_ID, HANDWRYTTEN_FONT_LABEL, rows)
    except HandwryttenError as e:
        log.exception("Handwrytten placeBasket failed")
        return json_response(
            502,
            {
                "message": "Could not add the cards to the Handwrytten basket; check the basket in the Handwrytten dashboard before retrying",
                "error": str(e),
            },
        )

    try:
        sent = hw_client.send_basket()
    except HandwryttenError as e:
        log.exception("Handwrytten basket/send failed")
        return json_response(
            502,
            {
                "message": "The cards are in the Handwrytten basket but checkout failed. Check out or clear the basket in the Handwrytten dashboard; don't just retry, or they'll be ordered twice.",
                "error": str(e),
            },
        )

    order_id = str((placed or {}).get("order_id") or "")
    log.info(f"handwrytten send complete count={len(letters)} order_id={order_id}")

    failed_to_mark = []
    if mark_sent:
        sent_at = datetime.now().isoformat()
        for letter in letters:
            letter.status = LetterStatus.SENT
            letter.handwrytten_order_id = order_id
            letter.sent_at = sent_at
            try:
                letter.update_db(dynamo_client)
            except Exception:
                log.exception(f"Failed to mark letter {letter.id} SENT")
                failed_to_mark.append(letter.id)

    body = {
        "message": f"sent {len(letters)} card(s) via Handwrytten",
        "dry_run": False,
        "count": len(letters),
        "handwrytten_order_id": order_id,
        "marked_sent": mark_sent,
        "letter_ids": [letter.id for letter in letters],
        "handwrytten_response": sent,
    }
    if failed_to_mark:
        # The cards WERE ordered; these just weren't marked. Resending them
        # would mail them twice, so set them to SENT by hand instead.
        body["failed_to_mark_sent"] = failed_to_mark
    return json_response(200, body)


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


def letter_body_too_long_response(letter_body):
    """400 Response if letter_body exceeds LETTER_BODY_MAX_CHARS, else None."""
    if letter_body and len(letter_body) > LETTER_BODY_MAX_CHARS:
        return Response(
            status_code=400,
            content_type="application/json",
            body={
                "message": f"letter_body is {len(letter_body)} characters; the max is {LETTER_BODY_MAX_CHARS}"
            },
        )
    return None


@app.get("/miatun/ping")
def ping():
    return Response(
        status_code=200,
        content_type="application/json",
        body={"message": "ping success"},
    )


def run_letters_sync(dynamo_client) -> tuple:
    """Recompute every letter from current claims/items/users (respecting
    disjoined-pair exceptions — see POST /miatun/disjoin), upsert
    contact/gift fields, and prune stale SYNC letters no longer matching any
    current household. Never overwrites letter_body/status on rows that
    already exist; manual letters are never touched. Shared by POST
    /miatun/sync and POST /miatun/disjoin so both stay consistent.

    :return: (letters, pruned_count)
    """
    received_items_by_id, claims, users_by_first_last, disjoined_pair_keys = (
        fetch_sync_data(dynamo_client)
    )
    letters = build_letter_records(
        received_items_by_id,
        claims,
        users_by_first_last,
        disjoined_pair_keys=disjoined_pair_keys,
    )
    for letter in letters:
        letter.sync_upsert_db(dynamo_client)

    current_ids = {letter.id for letter in letters}
    existing_letters = LetterRecord.get_all_letters_db(dynamo_client)
    pruned_count = 0
    for existing in existing_letters:
        if existing.source == "SYNC" and existing.id not in current_ids:
            existing.delete_db(dynamo_client)
            pruned_count += 1

    return letters, pruned_count


@app.post("/miatun/sync")
@validate_internal_route
def sync_letters():
    """Re-gather delivered gifts from claims/items/users and upsert them
    into the letters table. Never overwrites letter_body/status on rows
    that already exist. Also prunes SYNC-sourced letters that no longer
    correspond to any current household (e.g. a claim was removed, or the
    household grouping otherwise changed) — manual letters are never
    touched."""
    try:
        letters, pruned_count = run_letters_sync(CW_DYNAMO_CLIENT)

        log.info(
            f"letters sync complete synced_count={len(letters)} pruned_count={pruned_count}"
        )
        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "sync success",
                "synced_count": len(letters),
                "pruned_count": pruned_count,
            },
        )
    except Exception as e:
        log.exception("failed to sync letters")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to sync letters", "error": str(e)},
        )


@app.get("/miatun/letter")
@validate_internal_route
def list_letters():
    """
    Retrieve all letters from the database.
    """
    try:
        letters = LetterRecord.get_all_letters_db(CW_DYNAMO_CLIENT)
        letters_map = [letter.as_map() for letter in letters]

        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "letters retrieved successfully",
                "letters": letters_map,
            },
        )
    except Exception as e:
        log.exception("Failed to retrieve letters")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to retrieve letters", "error": str(e)},
        )


@app.post("/miatun/letter")
@validate_internal_route
def create_letter():
    """
    Manually create a letter not tied to a registry claim.
    """
    payload = app.current_event.json_body

    try:
        too_long = letter_body_too_long_response(payload.get("letter_body", ""))
        if too_long:
            return too_long

        letter = LetterRecord(
            id=str(uuid.uuid4()),
            guest=payload.get("guest", ""),
            partner=payload.get("partner", ""),
            claimant_id=payload.get("claimant_id", ""),
            gifts=payload.get("gifts", []),
            phone=payload.get("phone", ""),
            street=payload.get("street", ""),
            second_line=payload.get("second_line", ""),
            city=payload.get("city", ""),
            state_loc=payload.get("state_loc", ""),
            zipcode=payload.get("zipcode", ""),
            country=payload.get("country", ""),
            letter_body=payload.get("letter_body", ""),
            status=LetterStatus.DRAFT,
            source="MANUAL",
        )
        letter.update_db(CW_DYNAMO_CLIENT)

        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "success",
                "letter": letter.as_map(),
            },
        )
    except Exception as e:
        log.exception("Failed to create letter")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to create letter", "error": str(e)},
        )


@app.patch("/miatun/letter")
@validate_internal_route
def patch_letter():
    """
    Edit a letter (body text, status, or any contact/gift field). The
    letter id is passed in the JSON body as `letter_id`, matching
    spectaculo's PATCH /spectaculo/item convention.
    """
    payload = app.current_event.json_body
    letter_id = payload.get("letter_id")

    try:
        if not letter_id:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "letter_id is required"},
            )

        letter = LetterRecord.from_letter_id_db(letter_id, CW_DYNAMO_CLIENT)
        if not letter:
            return Response(
                status_code=404,
                content_type="application/json",
                body={"message": f"Letter with ID {letter_id} not found"},
            )

        editable_fields = [
            "guest",
            "partner",
            "claimant_id",
            "gifts",
            "phone",
            "street",
            "second_line",
            "city",
            "state_loc",
            "zipcode",
            "country",
            "letter_body",
        ]
        too_long = letter_body_too_long_response(payload.get("letter_body", ""))
        if too_long:
            return too_long

        for field in editable_fields:
            if field in payload:
                setattr(letter, field, payload[field])
        if "status" in payload:
            letter.status = LetterStatus[payload["status"]]

        letter.update_db(CW_DYNAMO_CLIENT)

        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "success",
                "letter": letter.as_map(),
            },
        )
    except Exception as e:
        log.exception(f"Failed to update letter {letter_id}")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to update letter", "error": str(e)},
        )


@app.delete("/miatun/letter")
@validate_internal_route
def delete_letter():
    """
    Delete a letter. The letter id is passed in the JSON body as
    `letter_id`, matching the PATCH convention above.
    """
    payload = app.current_event.json_body
    letter_id = (payload or {}).get("letter_id")

    try:
        if not letter_id:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "letter_id is required"},
            )

        letter = LetterRecord.from_letter_id_db(letter_id, CW_DYNAMO_CLIENT)
        if not letter:
            return Response(
                status_code=404,
                content_type="application/json",
                body={"message": f"Letter with ID {letter_id} not found"},
            )

        letter.delete_db(CW_DYNAMO_CLIENT)

        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "letter deleted successfully",
                "letter_id": letter_id,
            },
        )
    except Exception as e:
        log.exception(f"Failed to delete letter {letter_id}")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to delete letter", "error": str(e)},
        )


@app.post("/miatun/disjoin")
@validate_internal_route
def disjoin_letter_pair():
    """
    Split a two-person letter into two individual letters so a gift claimed
    by only one of a paired guest isn't implied as shared. Does NOT mutate
    guest_pair_first_last on the User table (that drives real RSVP
    date-pairing elsewhere) — instead records a durable exception in the
    letters_disjoined_pairs table that run_letters_sync() consults on every
    future sync, so the pair can't silently re-merge.

    Only source == "SYNC" letters with a resolvable claimant and a live
    partner pairing are supported; MANUAL letters (no stable claim identity
    to attribute gifts from, or to key a durable exception on) are
    rejected — edit those by hand via the existing letter CRUD routes.

    The letter id is passed in the JSON body as `letter_id`, matching the
    PATCH/DELETE convention above.
    """
    payload = app.current_event.json_body
    letter_id = (payload or {}).get("letter_id")

    try:
        if not letter_id:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "letter_id is required"},
            )

        letter = LetterRecord.from_letter_id_db(letter_id, CW_DYNAMO_CLIENT)
        if not letter:
            return Response(
                status_code=404,
                content_type="application/json",
                body={"message": f"Letter with ID {letter_id} not found"},
            )

        if letter.source != "SYNC":
            return Response(
                status_code=400,
                content_type="application/json",
                body={
                    "message": "Only claims-synced letters can be auto-disjoined; edit this manual letter's guest/partner fields (and create a second manual letter) by hand."
                },
            )

        if not letter.claimant_id:
            return Response(
                status_code=400,
                content_type="application/json",
                body={
                    "message": "This letter has no identifiable claimant to disjoin a partner from."
                },
            )

        user = get_user_db(CW_DYNAMO_CLIENT, letter.claimant_id)
        partner_id = user.get("guest_pair_first_last") or ""
        if not partner_id:
            return Response(
                status_code=400,
                content_type="application/json",
                body={
                    "message": "No partner is currently on file for this claimant; nothing to disjoin."
                },
            )

        pair_key = disjoined_pair_key(letter.claimant_id, partner_id)
        save_disjoined_pair_db(CW_DYNAMO_CLIENT, pair_key)

        # Preserve any in-progress draft before recompute rewrites letter ids.
        preserved_body = letter.letter_body
        preserved_status = letter.status
        original_claimant_id = letter.claimant_id

        letters, pruned_count = run_letters_sync(CW_DYNAMO_CLIENT)
        by_claimant_id = {l.claimant_id: l for l in letters}

        primary = by_claimant_id.get(original_claimant_id)
        partner = by_claimant_id.get(partner_id)
        # primary/partner can be None if that person personally claimed zero
        # gifts post-split — build_letter_records only creates a letter per
        # household with >=1 gift line, and no placeholder letter is created
        # for a zero-gift partner.

        if primary and (preserved_body or preserved_status != LetterStatus.DRAFT):
            primary.letter_body = preserved_body
            primary.status = preserved_status
            primary.update_db(CW_DYNAMO_CLIENT)

        log.info(f"disjoined pair pair_key={pair_key} pruned_count={pruned_count}")

        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "success",
                "letters": [l.as_map() for l in [primary, partner] if l],
            },
        )
    except Exception as e:
        log.exception(f"Failed to disjoin letter {letter_id}")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to disjoin letter pair", "error": str(e)},
        )


def request_payload() -> dict:
    """JSON body as a dict, tolerating an empty/missing body."""
    try:
        return app.current_event.json_body or {}
    except Exception:
        return {}


@app.post("/miatun/send")
@validate_internal_route
def send_ready_letters():
    """
    Mail every READY_TO_SEND letter through Handwrytten in one basket
    checkout (one order, so batch pricing applies). Not exposed in the UI.

    Body: {"dry_run": bool (default true), "mark_sent": bool (default true)}.
    Only a literal `false` turns dry_run off, so nothing is mailed by
    accident. mark_sent=false leaves statuses alone (for a rehearsal with
    Handwrytten's account test mode on).
    """
    payload = request_payload()
    dry_run = payload.get("dry_run", True) is not False
    mark_sent = payload.get("mark_sent", True) is not False

    try:
        letters = [
            letter
            for letter in LetterRecord.get_all_letters_db(CW_DYNAMO_CLIENT)
            if letter.status == LetterStatus.READY_TO_SEND
        ]
        if not letters:
            return json_response(400, {"message": "No letters are READY_TO_SEND"})
        letters.sort(key=lambda letter: letter.guest)

        return send_letters_via_handwrytten(
            letters, dry_run, mark_sent, get_handwrytten_client(), CW_DYNAMO_CLIENT
        )
    except Exception as e:
        log.exception("Failed to send letters")
        return json_response(500, {"message": "Failed to send letters", "error": str(e)})


@app.post("/miatun/send-one")
@validate_internal_route
def send_one_letter():
    """
    Mail a single letter through Handwrytten — e.g. a test card addressed to
    ourselves before the real batch. Uses the same path as /miatun/send.
    Works for any status except SENT, so a test letter never has to be
    READY_TO_SEND (and get swept into the batch). Not exposed in the UI.

    Body: {"letter_id": str, "dry_run": bool (default true),
           "mark_sent": bool (default true)}.
    """
    payload = request_payload()
    letter_id = payload.get("letter_id")
    dry_run = payload.get("dry_run", True) is not False
    mark_sent = payload.get("mark_sent", True) is not False

    try:
        if not letter_id:
            return json_response(400, {"message": "letter_id is required"})

        letter = LetterRecord.from_letter_id_db(letter_id, CW_DYNAMO_CLIENT)
        if not letter:
            return json_response(
                404, {"message": f"Letter with ID {letter_id} not found"}
            )
        if letter.status == LetterStatus.SENT:
            return json_response(
                409, {"message": f"Letter {letter_id} has already been sent"}
            )

        return send_letters_via_handwrytten(
            [letter], dry_run, mark_sent, get_handwrytten_client(), CW_DYNAMO_CLIENT
        )
    except Exception as e:
        log.exception(f"Failed to send letter {letter_id}")
        return json_response(500, {"message": "Failed to send letter", "error": str(e)})


# Fallback for unhandled routes
@app.get("/*")
@app.post("/*")
@app.patch("/*")
@app.delete("/*")
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
CW_DYNAMO_CLIENT = CWDynamoClient()
