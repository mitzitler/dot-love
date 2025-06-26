import json
import os
import random
import string
from datetime import datetime
import time
import traceback
from functools import wraps
from boto3.dynamodb.types import TypeDeserializer
import uuid
from enum import Enum
from datetime import datetime

from aws_lambda_powertools.event_handler import Response

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.api_gateway import (
    APIGatewayHttpResolver,
    ProxyEventType,
)
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
import stripe
import requests

# Environment Variables for Stripe
# TODO: Configure these environment variables in the CDK stack:
# 1. STRIPE_SECRET - your Stripe API key for creating payments
# 2. STRIPE_WEBHOOK_SECRET - secret for verifying webhooks from Stripe
# 3. API_KEY - internal API key for communicating with gizmo service
STRIPE_SECRET = os.environ.get("stripe_secret", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("stripe_webhook_secret", "")
INTERNAL_API_KEY = os.environ.get("internal_api_key", "")
stripe.api_key = STRIPE_SECRET

# Environment Variables
REGISTRY_ITEM_TABLE_NAME = os.environ["registry_item_table_name"]
REGISTRY_CLAIM_TABLE_NAME = os.environ["registry_claim_table_name"]
API_BASE_URL = os.environ.get("api_base_url", "https://api.mitzimatthew.love")
MITZI_MATTHEW_ADDRESS = os.environ.get("mitzi_matthew_address")
INTERNAL_ROUTE_LIST = ["list", "ping"]

# Powertools logger
log = Logger(service="spectaculo")

# Powertools routing
app = APIGatewayHttpResolver()


########################################################
# Gizmo Service Client
########################################################
def send_text_notification(first_last, template_type, template_details):
    """
    Send a text notification via Gizmo service.

    :param first_last: User ID in first_last format to send text to
    :param template: The text template to use (raw text)
    :param template_details: Dict of values to format into the template
    :return: Response from Gizmo service
    """
    try:
        # Prepare the request to Gizmo service
        gizmo_endpoint = f"{API_BASE_URL}/gizmo/text"
        payload = {
            "is_blast": False,
            "template_type": template_type,
            "template_details": template_details,
            # NOTE: Will be looked up by Gizmo based on first_last
            "recipient_phone": None,
            "trace": app.context.get("trace_id", "🤷"),
        }

        headers = {
            "Content-Type": "application/json",
            "Internal-Api-Key": INTERNAL_API_KEY,
            "X-First-Last": first_last,
        }

        # Send the request to Gizmo
        log.info(f"Sending text notification to {first_last}")
        response = requests.post(gizmo_endpoint, json=payload, headers=headers)

        if response.status_code != 200:
            log.error(f"Failed to send text notification to Gizmo: {response.text}")
            return False

        log.info(f"Successfully sent text notification to {first_last}")
        return True
    except Exception as e:
        log.exception(f"Error sending text notification: {str(e)}")
        return False


########################################################
# Supporting Classes
########################################################
class ClaimState(Enum):
    CLAIMED = 1
    PURCHASED = 2
    UNCLAIMED = 3

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"ClaimState.{self.name}"


class RegistryItem:
    def __init__(
        self,
        item_id,
        name,
        last_checked,
        brand,
        descr,
        size_score,
        art_score,
        link,
        img_url,
        price_cents,
        claim_state,
        display,
        claimant_id=None,
        received=False,
    ):
        """
        Initialize a RegistryItem, to track the stuff people will buy from us!

        :param item_id (STR): uuid.
        :param name (STR): name of the item being claimed.
        :param last_checked (DATETIME): datetime of the last time we checked on the availability of this item.
        :param brand (STR): brand of the item.
        :param descr (STR): a description of the item.
        :param size_score (INT): used by the frontend to decide where the item falls on the size axis.
        :param art_score (INT): used by the frontend to decide where the item falls on the function axis.
        :param link (STR): url to the item.
        :param img_url (STR): s3 url for the item.
        :param price_cents (INT): cost of the item, in cents.
        :param claim_state (ClaimState): ClaimState of the item - Claimed, Purchased, or Unclaimed.
        :param display (BOOL): whether the FE should display the item.
        :param claimant_id (STR): User id of the person who has claimed the item.
        :param received (BOOL): whether the item has been received by us or not
        """
        self.item_id = item_id
        self.name = name
        self.last_checked = last_checked
        self.brand = brand
        self.descr = descr
        self.size_score = size_score
        self.art_score = art_score
        self.link = link
        self.img_url = img_url
        self.price_cents = price_cents
        self.claim_state = claim_state
        self.display = display
        self.claimant_id = claimant_id
        self.received = received

    def as_map(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "last_checked": self.last_checked,
            "brand": self.brand,
            "descr": self.descr,
            "size_score": self.size_score,
            "art_score": self.art_score,
            "link": self.link,
            "img_url": self.img_url,
            "price_cents": self.price_cents,
            "claim_state": self.claim_state.name if self.claim_state else None,
            "display": self.display,
            "claimant_id": self.claimant_id,
            "received": self.received,
        }

    def __str__(self):
        return (
            f"RegistryItem(item_id={self.item_id}, name={self.name}, "
            f"brand={self.brand}, claim_state={self.claim_state}, claimant_id={self.claimant_id})"
        )

    def __repr__(self):
        return (
            f"RegistryItem(item_id={self.item_id!r}, name={self.name!r}, "
            f"brand={self.brand!r}, claim_state={self.claim_state!r}, claimant_id={self.claimant_id!r})"
        )

    @staticmethod
    def from_db(item_data):
        """
        Create a RegistryItem object from DynamoDB data.
        """
        if not item_data:
            return None

        # Convert DynamoDB types to Python types
        deserializer = TypeDeserializer()
        deserialized_item = {
            k: deserializer.deserialize(v) for k, v in item_data.items()
        }

        claim_state_str = deserialized_item.get("claim_state", "UNCLAIMED")
        claim_state = (
            ClaimState[claim_state_str] if claim_state_str else ClaimState.UNCLAIMED
        )

        return RegistryItem(
            item_id=deserialized_item.get("id"),
            name=deserialized_item.get("item_name"),
            last_checked=deserialized_item.get("last_checked"),
            brand=deserialized_item.get("brand"),
            descr=deserialized_item.get("descr"),
            size_score=float(deserialized_item.get("size_score", 0.0)),
            art_score=float(deserialized_item.get("art_score", 0.0)),
            link=deserialized_item.get("link"),
            img_url=deserialized_item.get("img_url"),
            price_cents=int(deserialized_item.get("price_cents", 0)),
            claim_state=claim_state,
            display=deserialized_item.get("display", True),
            claimant_id=deserialized_item.get("claimant_id", "").lower(),
            received=deserialized_item.get("received", False),
        )

    @staticmethod
    def from_item_id_db(item_id, dynamo_client):
        """
        Get a registry item from the database by its ID.

        :param item_id: The ID of the registry item
        :param dynamo_client: The DynamoDB client
        :return: RegistryItem object or None if not found
        """
        try:
            key_expression = {"id": {"S": item_id}}
            item_data = dynamo_client.get(REGISTRY_ITEM_TABLE_NAME, key_expression)

            if not item_data:
                log.info(f"No registry item found with ID: {item_id}")
                return None

            return RegistryItem.from_db(item_data)
        except Exception as e:
            log.exception(f"Error retrieving registry item with ID {item_id}: {str(e)}")
            return None

    @staticmethod
    def get_all_items_db(dynamo_client):
        """
        Get all registry items from the database.

        :param dynamo_client: The DynamoDB client
        :return: List of RegistryItem objects
        """
        try:
            items_data = dynamo_client.get_all(REGISTRY_ITEM_TABLE_NAME)

            registry_items = []
            for item_data in items_data:
                item = RegistryItem.from_db(item_data)
                if item:
                    registry_items.append(item)

            return registry_items
        except Exception as e:
            log.exception(f"Error retrieving all registry items: {str(e)}")
            return []

    def update_db(self, dynamo_client):
        """
        Update this registry item in the database.
        """
        key_expression = {"id": {"S": self.item_id}}
        field_value_map = {
            "item_name": self.name,
            "last_checked": self.last_checked,
            "brand": self.brand,
            "descr": self.descr,
            "size_score": self.size_score,
            "art_score": self.art_score,
            "link": self.link,
            "img_url": self.img_url,
            "price_cents": self.price_cents,
            "display": self.display,
            "claim_state": (
                self.claim_state.name if self.claim_state else ClaimState.UNCLAIMED.name
            ),
            "received": self.received,
        }

        # Only include claimant_id if it's not None
        if self.claimant_id:
            field_value_map["claimant_id"] = self.claimant_id

        res = dynamo_client.update(
            REGISTRY_ITEM_TABLE_NAME,
            key_expression,
            field_value_map,
        )

        return res


class RegistryClaim:
    def __init__(self, item_id, claimant_id, claim_state, updated_at=None, id=None):
        """
        Initialize a RegistryClaim, to keep track of who has claimed what.

        :param item_id(UUID): id of the Registry item that has been claimed.
        :param claimant_id(STR): Primary key for the user (first_last format, e.g., "john_smith").
        :param claim_state (ClaimState): ClaimState of the item - Claimed, Purchased, or Unclaimed.
        :param updated_at(DATETIME): datetime of the last time this record was updated.
        """
        if id:
            self.id = id
        else:
            self.id = str(uuid.uuid4())

        self.item_id = item_id
        self.claimant_id = claimant_id
        self.claim_state = claim_state
        self.updated_at = updated_at or datetime.now().isoformat()

    def as_map(self):
        return {
            "id": self.id,
            "item_id": self.item_id,
            "claimant_id": self.claimant_id,
            "claim_state": self.claim_state.name if self.claim_state else None,
            "updated_at": self.updated_at,
        }

    def __str__(self):
        return (
            f"RegistryClaim(id={self.id}, item_id={self.item_id}, "
            f"claimant_id={self.claimant_id}, claim_state={self.claim_state})"
        )

    def __repr__(self):
        return (
            f"RegistryClaim(id={self.id!r}, item_id={self.item_id!r}, "
            f"claimant_id={self.claimant_id!r}, claim_state={self.claim_state!r})"
        )

    def create_db(self, dynamo_client):
        """
        Create this registry claim in the database.
        """
        key_expression = {"id": {"S": self.id}}
        field_value_map = {
            "item_id": self.item_id,
            "claimant_id": self.claimant_id,
            "claim_state": self.claim_state.name,
            "updated_at": self.updated_at,
        }

        res = dynamo_client.create(
            REGISTRY_CLAIM_TABLE_NAME,
            key_expression,
            field_value_map,
        )

        return res

    def update_db(self, dynamo_client):
        """
        Update this registry claim in the database.
        """
        key_expression = {"id": {"S": self.id}}
        field_value_map = {
            "item_id": self.item_id,
            "claimant_id": self.claimant_id,
            "claim_state": self.claim_state.name,
            "updated_at": datetime.now().isoformat(),
        }

        res = dynamo_client.update(
            REGISTRY_CLAIM_TABLE_NAME,
            key_expression,
            field_value_map,
        )

        return res

    @staticmethod
    def from_db(claim_data):
        """
        Create a RegistryClaim object from DynamoDB data.

        :param claim_data: The DynamoDB data
        :return: RegistryClaim object or None if not found
        """
        if not claim_data:
            return None

        # Convert DynamoDB types to Python types
        deserializer = TypeDeserializer()
        claim = {k: deserializer.deserialize(v) for k, v in claim_data.items()}

        try:
            return RegistryClaim(
                item_id=claim.get("item_id"),
                claimant_id=claim.get("claimant_id"),
                claim_state=ClaimState[claim.get("claim_state")],
                updated_at=claim.get("updated_at"),
                id=claim.get("id"),
            )
        except Exception as e:
            log.exception(f"Error creating RegistryClaim from data: {e}")
            return None

    @staticmethod
    def find_by_item_id(item_id, dynamo_client):
        """
        Find registry claim by item ID.

        :param item_id: The item id UUID
        :param dynamo_client: The DynamoDB client
        :return: RegistryClaim object or None if not found
        """
        try:
            claim_items = dynamo_client.query(
                table_name=REGISTRY_CLAIM_TABLE_NAME,
                index_name="item-id-lookup-index",
                key_condition_expression="item_id = :item_id",
                expression_attribute_values={":item_id": {"S": item_id}},
            )

            if not claim_items:
                log.error("No claims found", item=item_id)
                return None

            # Use the first matching item
            claim = RegistryClaim.from_db(claim_items[0])
            return claim

        except Exception as e:
            log.exception(f"Error finding registry claim by item_id: {e}")
            return None

    @staticmethod
    def find_by_user_id(first_last, dynamo_client):
        """
        Find registry claims by user ID (first_last).

        :param first_last: The user ID (first_last)
        :param dynamo_client: The DynamoDB client
        :return: List of RegistryClaim objects
        """
        try:
            # Query the registry claims using the GSI
            claims_data = dynamo_client.query(
                table_name=REGISTRY_CLAIM_TABLE_NAME,
                index_name="claimant-id-lookup-index",
                key_condition_expression="claimant_id = :claimant_id",
                expression_attribute_values={":claimant_id": {"S": first_last}},
            )

            if not claims_data:
                return []

            # Convert all claims to RegistryClaim objects
            registry_claims = []
            for claim_data in claims_data:
                claim = RegistryClaim.from_db(claim_data)
                if claim:
                    registry_claims.append(claim)

            return registry_claims
        except Exception as e:
            log.exception(f"Error finding registry claims by user_id: {e}")
            return []

    @staticmethod
    def claim_list_db(dynamo_client):
        """
        Get all registry claims from the database.

        :param dynamo_client: The DynamoDB client
        :return: List of RegistryItem objects
        """
        try:
            # Query the registry claims using the GSI
            claims_data = dynamo_client.get_all(REGISTRY_CLAIM_TABLE_NAME)

            claim_items = []
            for raw_claim in claims_data:
                claim = RegistryClaim.from_db(raw_claim)
                if claim:
                    claim_items.append(claim)

            return claim_items
        except Exception as e:
            log.exception(f"Error retrieving all claim items: {str(e)}")
            return []


########################################################
# CWDynamo Client
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
        update_expression = self.format_update_expression(
            [*field_value_map.keys()]
            + (
                []
                if manual_expression_attribute_map is None
                else [*manual_expression_attribute_map.keys()]
            )
        )

        expression_attribute_values = self.format_update_expression_attribute_values(
            field_value_map, manual_expression_attribute_map, operation="update"
        )

        res = self.client.update_item(
            TableName=table_name,
            Key=key_expression,
            UpdateExpression=update_expression,
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

        # Add filter if provided
        if filter_expression:
            scan_kwargs["FilterExpression"] = filter_expression
            if expression_attribute_values:
                scan_kwargs["ExpressionAttributeValues"] = expression_attribute_values

        # Initialize results list and pagination variables
        items = []
        last_evaluated_key = None

        # Paginate through results
        while True:
            # Include ExclusiveStartKey if we're continuing from a previous page
            if last_evaluated_key:
                scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

            # Execute the scan
            response = self.client.scan(**scan_kwargs)

            # Add items from this page
            items.extend(response.get("Items", []))

            # Check if there are more pages
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

            # Add logging for large datasets
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

        # Initialize variables for pagination
        projection_items = []
        last_evaluated_key = None

        # Paginate through results
        while True:
            # Set up scan parameters
            scan_kwargs = {"TableName": table_name, "ProjectionExpression": col_name}

            # Include ExclusiveStartKey if we're continuing from a previous page
            if last_evaluated_key:
                scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

            # Execute the scan
            response = self.client.scan(**scan_kwargs)

            # Process items from this page
            items = response.get("Items", [])
            for item in items:
                deserialized_item = {
                    k: deserializer.deserialize(v) for k, v in item.items()
                }
                projection_items.append(deserialized_item)

            # Check if there are more pages
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

            # Add logging for large datasets
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

        # Add index name if provided
        if index_name:
            query_kwargs["IndexName"] = index_name

        # Initialize results list and pagination variables
        items = []
        last_evaluated_key = None

        # Paginate through results
        while True:
            # Include ExclusiveStartKey if we're continuing from a previous page
            if last_evaluated_key:
                query_kwargs["ExclusiveStartKey"] = last_evaluated_key

            # Execute the query
            response = self.client.query(**query_kwargs)

            # Add items from this page
            items.extend(response.get("Items", []))

            # Check if there are more pages
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

            # Add logging for large datasets
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

    def batch_get_items(self, table_name, keys, projection_expression=None):
        """
        Get multiple items from a DynamoDB table in a batch operation with automatic handling
        of DynamoDB's batch size limit (100 items).

        :param table_name: Name of the DynamoDB table
        :param keys: List of key dictionaries to get
        :param projection_expression: Optional projection expression to limit attributes returned
        :return: List of all matching items
        """
        # DynamoDB batch operations are limited to 100 items at a time
        MAX_BATCH_SIZE = 100

        # Initialize results
        all_items = []

        # Process in batches of MAX_BATCH_SIZE
        for i in range(0, len(keys), MAX_BATCH_SIZE):
            batch_keys = keys[i : i + MAX_BATCH_SIZE]

            request_items = {table_name: {"Keys": batch_keys}}

            # Add projection expression if provided
            if projection_expression:
                request_items[table_name][
                    "ProjectionExpression"
                ] = projection_expression

            # Execute the batch get
            response = self.client.batch_get_item(RequestItems=request_items)

            # Add returned items to results
            if table_name in response.get("Responses", {}):
                all_items.extend(response["Responses"][table_name])

            # Handle unprocessed keys (with exponential backoff)
            unprocessed_keys = response.get("UnprocessedKeys", {})
            retry_count = 0
            max_retries = 5
            base_delay = 0.05  # 50 milliseconds

            while (
                unprocessed_keys
                and table_name in unprocessed_keys
                and retry_count < max_retries
            ):
                # Exponential backoff
                delay = base_delay * (2**retry_count)
                time.sleep(delay)

                # Retry the unprocessed keys
                retry_response = self.client.batch_get_item(
                    RequestItems=unprocessed_keys
                )

                # Add new returned items
                if table_name in retry_response.get("Responses", {}):
                    all_items.extend(retry_response["Responses"][table_name])

                # Update unprocessed keys for next iteration
                unprocessed_keys = retry_response.get("UnprocessedKeys", {})
                retry_count += 1

            # Log warning if we still have unprocessed keys after max retries
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
                # add semicolon to manual_attribute_map keys
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

        # Handle specific data types
        if dynamoType == "N" and (
            isinstance(field_value, int) or isinstance(field_value, float)
        ):
            dynamoValue = str(field_value)
        elif dynamoType == "BOOL" and isinstance(field_value, str):
            dynamoValue = field_value == "True"
        elif dynamoType == "NULL":
            dynamoValue = True  # For NULL type, value is always true
        elif dynamoType == "M" and isinstance(field_value, dict):
            # Handle map type by recursively formatting each item
            dynamoValue = self._format_map_for_dynamo(field_value)
        elif dynamoType == "L" and isinstance(field_value, list):
            # Handle list type by recursively formatting each item
            dynamoValue = self._format_list_for_dynamo(field_value)
        elif dynamoType in ("SS", "NS") and isinstance(field_value, list):
            # Handle string and number sets
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
            if not value:  # Empty list
                return "L"
            if all(isinstance(x, str) for x in value):
                return "SS"
            elif all(isinstance(x, (int, float)) for x in value):
                return "NS"
            else:
                return "L"  # Mixed type list

        raise Exception(
            f"CWDynamo Client Error: Unhandled data type provided for value: {value}"
        )

    def format_update_expression(self, field_name_list):
        if not field_name_list:
            raise ValueError("No fields provided for update expression")

        update_expression = f"SET {field_name_list[0]} = :{field_name_list[0]}"
        remaining_fields = field_name_list[1:]

        for field_name in remaining_fields:
            update_expression = update_expression + f", {field_name} = :{field_name}"

        return update_expression


########################################################
# Payment Processing
########################################################
def create_payment_intent(amount, metadata=None, payment_method_types=None):
    """
    Create a Stripe PaymentIntent.

    :param amount: Amount in cents
    :param metadata: Optional metadata to attach to the payment
    :param payment_method_types: Optional list of payment method types
    :return: PaymentIntent object
    """
    try:
        params = {
            "amount": amount,
            "currency": "usd",
            "automatic_payment_methods": {"enabled": True},
        }

        if metadata:
            params["metadata"] = metadata

        if payment_method_types:
            params["payment_method_types"] = payment_method_types

        payment_intent = stripe.PaymentIntent.create(**params)

        log.info(f"Created PaymentIntent: {payment_intent.id}")
        return payment_intent
    except stripe.error.StripeError as e:
        log.error(f"Stripe error: {str(e)}")
        raise
    except Exception as e:
        log.error(f"Error creating payment intent: {str(e)}")
        raise


def handle_stripe_webhook(event_data, signature_header=None, webhook_secret=None):
    """
    Process a Stripe webhook event.

    :param event_data: The raw event data
    :param signature_header: Optional Stripe signature header for verification
    :param webhook_secret: Optional webhook secret for verification
    :return: Processed event object
    """
    try:
        # Verify webhook signature if provided
        if signature_header and webhook_secret:
            event = stripe.Webhook.construct_event(
                payload=event_data, sig_header=signature_header, secret=webhook_secret
            )
        else:
            log.warn("no webhook secret included")
            event = stripe.Event.construct_from(
                json.loads(event_data) if isinstance(event_data, str) else event_data,
                stripe.api_key,
            )

        log.info(f"Processing webhook event type: {event.type}")

        # Handle the event based on its type
        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            log.info(f"Payment succeeded: {payment_intent.id}")

            # Get metadata to identify the user who made the payment
            metadata = payment_intent.metadata
            first_last = metadata.get("user_id", "guest")
            amount_dollars = payment_intent.amount / 100

            # Send a text notification to the user and us
            if first_last != "guest":
                send_text_notification()

        elif event.type == "payment_intent.payment_failed":
            payment_intent = event.data.object
            log.info(f"Payment failed: {payment_intent.id}")

        return event
    except ValueError as e:
        log.error(f"Invalid payload: {str(e)}")
        raise
    except stripe.error.SignatureVerificationError as e:
        log.error(f"Invalid signature: {str(e)}")
        raise
    except Exception as e:
        log.error(f"Error processing webhook: {str(e)}")
        raise


########################################################
# API Endpoints
########################################################
def validate_internal_route(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        event = app.current_event
        api_key = event.headers.get("Internal-Api-Key")

        if not api_key or api_key != INTERNAL_API_KEY:
            return Response(
                status_code=401,
                content_type="application/json",
                body={"message": "no valid api key"},
            )

        return func(*args, **kwargs)

    return wrapper


@app.get("/spectaculo/item")
def get_registry_items():
    """
    Retrieve all registry items from the database.
    """
    try:
        # Get all registry items using the static method
        registry_items = RegistryItem.get_all_items_db(CW_DYNAMO_CLIENT)

        if not registry_items:
            # This shouldn't happen
            return Response(
                status_code=500,
                content_type="application/json",
                body={"message": "No registry items found", "items": []},
            )

        # Convert to map representation for API response
        registry_items_map = [item.as_map() for item in registry_items]

        # Using Response class from Lambda Powertools
        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "Registry items retrieved successfully",
                "items": registry_items_map,
            },
        )
    except Exception as e:
        log.exception("Failed to retrieve registry items")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to retrieve registry items", "error": str(e)},
        )


@app.post("/spectaculo/item")
def add_registry_item():
    """
    Add an item to the registry.
    """
    payload = app.current_event.json_body

    try:
        # Get the registry item using the static method
        item = RegistryItem(
            item_id=str(uuid.uuid4()),
            name=payload.get("name"),
            last_checked=datetime.now().strftime("%m/%d/%Y"),
            brand=payload.get("brand"),
            descr=payload.get("descr"),
            size_score=payload.get("size_score"),
            art_score=payload.get("art_score"),
            link=payload.get("link"),
            img_url=payload.get("img_url"),
            display=payload.get("display"),
            price_cents=payload.get("price_cents"),
            claim_state=ClaimState.UNCLAIMED,
            received=payload.get("display", False),
        )
        item.update_db(CW_DYNAMO_CLIENT)
        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "success",
                "item": item.as_map(),
            },
        )
    except Exception as e:
        log.exception("Failed to create registry claim")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to create registry claim", "error": str(e)},
        )


@app.patch("/spectaculo/item")
def patch_registry_item():
    """
    Update an item to in registry.
    """
    payload = app.current_event.json_body

    try:
        # Get the registry item
        item = RegistryItem.from_item_id_db(payload.get("item_id"), CW_DYNAMO_CLIENT)

        # update the values
        item.price_cents = payload.get("price_cents")
        item.last_checked = datetime.now().strftime("%m/%d/%Y")
        item.update_db(CW_DYNAMO_CLIENT)

        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "success",
                "item": item.as_map(),
            },
        )
    except Exception as e:
        log.exception("Failed to update registry item")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to update registry item", "error": str(e)},
        )


@app.get("/spectaculo/item/<item_id>")
def get_registry_item(item_id):
    """
    Retrieve a specific registry item by ID.
    """
    try:
        # Get the registry item using the static method
        item = RegistryItem.from_item_id_db(item_id, CW_DYNAMO_CLIENT)

        if not item:
            return Response(
                status_code=404,
                content_type="application/json",
                body={"message": f"Registry item with ID {item_id} not found"},
            )

        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "Registry item retrieved successfully",
                "item": item.as_map(),
            },
        )
    except Exception as e:
        log.exception(f"Failed to retrieve registry item with ID {item_id}")
        return Response(
            status_code=500,
            content_type="application/json",
            body={
                "message": f"Failed to retrieve registry item with ID {item_id}",
                "error": str(e),
            },
        )


@app.post("/spectaculo/claim")
def create_claim():
    """
    Create a registry claim in the db. This method extracts an item_id and a claimant_id
    from the passed in json, and uses this to create a RegistryClaim (with claim_state: CLAIMED)
    """
    try:
        payload = app.current_event.json_body
        item_id = payload.get("item_id")
        claimant_id = payload.get("claimant_id").lower()

        if not item_id or not claimant_id:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "Item ID and claimant ID are required"},
            )

        # Check if the item exists
        item = RegistryItem.from_item_id_db(item_id, CW_DYNAMO_CLIENT)

        if not item:
            return Response(
                status_code=404,
                content_type="application/json",
                body={"message": f"Registry item with ID {item_id} not found"},
            )

        # Check if the item is already claimed
        if (
            item.claim_state is ClaimState.CLAIMED
            or item.claim_state is ClaimState.PURCHASED
        ):
            return Response(
                status_code=400,
                content_type="application/json",
                body={
                    "message": f"Registry item with ID {item_id} is already {item.claim_state.name.lower()}"
                },
            )

        # Check if there's already a claim for this item
        existing_claim = RegistryClaim.find_by_item_id(item_id, CW_DYNAMO_CLIENT)
        if existing_claim:
            if existing_claim.claim_state is ClaimState.CLAIMED:
                return Response(
                    status_code=409,
                    content_type="application/json",
                    body={
                        "message": f"Registry item with ID {item_id} already has a claim by user {existing_claim.claimant_id}"
                    },
                )
            else:
                # Update the existing unclaimed claim to CLAIMED
                existing_claim.claim_state = ClaimState.CLAIMED
                existing_claim.claimant_id = claimant_id
                existing_claim.update_db(CW_DYNAMO_CLIENT)
                registry_claim = existing_claim
        else:
            # Create registry claim
            registry_claim = RegistryClaim(
                item_id=item_id, claimant_id=claimant_id, claim_state=ClaimState.CLAIMED
            )

            registry_claim.create_db(CW_DYNAMO_CLIENT)

        # Update the registry item with the claim state and claimant ID
        item.claim_state = ClaimState.CLAIMED
        item.claimant_id = claimant_id
        item.update_db(CW_DYNAMO_CLIENT)

        # Send text notification to the claimant
        send_text_notification(
            first_last=claimant_id,
            template_type="ITEM_CLAIMED_TEXT",
            template_details={
                "item_name": item.name,
                "first_name": claimant_id.split("_")[0],
                "mitzi_matthew_address": MITZI_MATTHEW_ADDRESS,
            },
        )

        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "Registry claim created successfully",
                "claim": registry_claim.as_map(),
                "item": item.as_map(),
            },
        )
    except Exception as e:
        log.exception("Failed to create registry claim")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to create registry claim", "error": str(e)},
        )


@app.patch("/spectaculo/claim")
def update_claim():
    """
    Update a registry claim in the db. This method extracts an item_id and a claim_state from the
    passed in json, and applies the claim_state passed in to the item_id.

    If the claim_state passed in is UNCLAIMED, then the claimant_id is removed from the record.
    """
    try:
        payload = app.current_event.json_body
        item_id = payload.get("item_id")
        claim_state_str = payload.get("claim_state")

        if not item_id or not claim_state_str:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "Item ID and claim state are required"},
            )

        try:
            claim_state = ClaimState[claim_state_str.upper()]
        except (KeyError, AttributeError):
            return Response(
                status_code=400,
                content_type="application/json",
                body={
                    "message": f"Invalid claim state: {claim_state_str}. Must be one of: CLAIMED, PURCHASED, UNCLAIMED"
                },
            )

        # Check if the item exists
        item = RegistryItem.from_item_id_db(item_id, CW_DYNAMO_CLIENT)

        if not item:
            return Response(
                status_code=404,
                content_type="application/json",
                body={"message": f"Registry item with ID {item_id} not found"},
            )

        # Find the existing claim
        existing_claim = RegistryClaim.find_by_item_id(item_id, CW_DYNAMO_CLIENT)

        if not existing_claim:
            return Response(
                status_code=404,
                content_type="application/json",
                body={"message": f"No existing claim found for item with ID {item_id}"},
            )

        # If unclaiming, remove the claimant ID from the item
        if claim_state == ClaimState.UNCLAIMED:
            item.claimant_id = None

        item.claim_state = claim_state

        # Update the item
        item.update_db(CW_DYNAMO_CLIENT)

        # Update the claim if it exists
        existing_claim.claim_state = claim_state
        existing_claim.update_db(CW_DYNAMO_CLIENT)

        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": f"Registry claim updated successfully to {claim_state.name}",
                "claim": existing_claim.as_map(),
            },
        )
    except Exception as e:
        log.exception("Failed to update registry claim")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to update registry claim", "error": str(e)},
        )


@app.get("/spectaculo/claim")
def get_user_claims():
    """
    Retrieve all registry claims for a specific user.
    """
    first_last = app.context.get("first_last", "guest")
    try:
        first_last = app.context.get("first_last", "guest")

        # Get claims for the user
        raw_claims = RegistryClaim.find_by_user_id(first_last, CW_DYNAMO_CLIENT)
        if not raw_claims:
            return Response(
                status_code=200,
                content_type="application/json",
                body={
                    "message": f"No claims found for user {first_last}",
                    "claims": [],
                },
            )

        claims = [claim.as_map() for claim in raw_claims]
        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "User claims retrieved successfully",
                "claims": claims,
            },
        )
    except Exception as e:
        log.exception(f"Failed to retrieve claims for user {first_last}")
        return Response(
            status_code=500,
            content_type="application/json",
            body={
                "message": f"Failed to retrieve claims for user {first_last}",
                "error": str(e),
            },
        )


# get a list of all claims
@validate_internal_route
@app.get("/spectaculo/claim/list")
def list_claims():
    """
    Get a list of all claims and their ids
    """
    try:
        raw_claims = RegistryClaim.claim_list_db(CW_DYNAMO_CLIENT)

    except Exception as e:
        err_msg = "failed to list claims from db"
        log.exception(err_msg)
        return Response(
            status_code=500,
            content_type="application/json",
            body={
                "message": err_msg,
                "error": str(e),
            },
        )

    claim_maps = []
    for claim in raw_claims:
        claim_maps.append(claim.as_map())

        "body": {
        },
    }
    return Response(
        status_code=200,
        content_type="application/json",
        body={
            "message": "list claims success",
            "claims": claim_maps,
        },
    )


@app.post("/spectaculo/payment")
def payment_create():
    """
    Create a payment intent using Stripe.

    Expected JSON body:
    {
        "amount": 5000,  // Amount in cents
        "description": "Wedding gift",  // Optional description
        "user_id": "john_smith"  // Optional user identifier
    }
    """
    try:
        payload = app.current_event.json_body
        amount = payload.get("amount")
        description = payload.get("description", "Wedding registry payment")
        user_id = payload.get("user_id", app.context.get("first_last", "guest"))

        if not amount:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "Amount is required"},
            )

        if not isinstance(amount, int) or amount <= 0:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "Amount must be a positive integer (in cents)"},
            )

        metadata = {
            "description": description,
            "user_id": user_id,
            "source": "registry",
        }

        # Create the payment intent
        payment_intent = create_payment_intent(amount=amount, metadata=metadata)

        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": "Payment intent created successfully",
                "client_secret": payment_intent.client_secret,
                "payment_intent_id": payment_intent.id,
                "amount": amount,
            },
        )
    except stripe.error.StripeError as e:
        log.exception(f"Stripe error occurred: {str(e)}")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": f"Stripe error: {str(e)}"},
        )
    except Exception as e:
        log.exception(f"Failed to create payment intent: {str(e)}")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to create payment intent", "error": str(e)},
        )


@app.post("/spectaculo/payment/webhook")
def payment_webhook():
    """
    Handle Stripe webhook events for payment intents.
    """
    try:
        # Get the webhook data
        payload = app.current_event.body
        signature_header = app.current_event.headers.get("Stripe-Signature")

        # Get webhook secret from environment variable
        # In production, this should be set in your Lambda env variables
        webhook_secret = STRIPE_WEBHOOK_SECRET

        # Process the webhook event
        event = handle_stripe_webhook(
            event_data=payload,
            signature_header=signature_header,
            webhook_secret=webhook_secret,
        )

        # Return a success response to Stripe
        return Response(
            status_code=200,
            content_type="application/json",
            body={"message": "Webhook received and processed"},
        )
    except ValueError as e:
        log.exception(f"Invalid webhook payload: {str(e)}")
        return Response(
            status_code=400,
            content_type="application/json",
            body={"message": f"Invalid webhook payload: {str(e)}"},
        )
    except stripe.error.SignatureVerificationError as e:
        log.exception(f"Invalid webhook signature: {str(e)}")
        return Response(
            status_code=400,
            content_type="application/json",
            body={"message": f"Invalid webhook signature: {str(e)}"},
        )
    except Exception as e:
        log.exception(f"Error processing webhook: {str(e)}")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": f"Error processing webhook: {str(e)}"},
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
    # Exclude middleware for stripe webhook
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
    first_last = event["headers"].get("x-first-last").lower()
    if not first_last:
        log.error("First and last name not included in headers")
        return {"code": 400, "message": "First and last name not included in headers"}
    log.append_keys(first_last=first_last)
    app.append_context(first_last=first_last)

    return handler(event, context)


@log.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_HTTP, log_event=True
)
@middleware_before
def handler(event, context):
    try:
        return app.resolve(event, context)
    except Exception as e:
        log.exception("unhandled server error encountered")
        return {"code": 500, "message": "Unhandled server error encountered"}


# NOTE: Doing this at the top level so the client connections are preserved b/t lambda calls
# Initialize clients
CW_DYNAMO_CLIENT = CWDynamoClient()
