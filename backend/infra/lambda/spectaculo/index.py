import os
import json
import traceback
import stripe
import boto3
import hashlib
import logging
from enum import Enum
from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.idempotency import (
    DynamoDBPersistenceLayer,
    IdempotencyConfig,
    idempotent_function,
)

# Environment Variables
USER_TABLE_NAME = os.environ["user_table_name"]
COMMODITY_TABLE_NAME = os.environ["commodity_table_name"]
TRANSACTION_TABLE_NAME = os.environ["transaction_table_name"]
TRANSACTION_EMAIL_CACHE_NAME = os.environ["transaction_email_cache_s3_name"]
SES_CONFIG_ID = os.environ["ses_config_id"]
SES_SENDER_EMAIL = os.environ["ses_sender_email"]
SES_ADMIN_LIST = os.environ["ses_admin_list"].split(",")
stripe.api_key = os.environ["stripe_secret"]

# Logging
log = Logger(service="commerce")

# AWS Powertools
# idempotency_config = IdempotencyConfig(event_key_jmespath="order_id")

# Clients
S3_CLIENT = boto3.client("s3")
SES_CLIENT = boto3.client("ses")

# TODO: source from env vars
SHIPPING_WEIGHT_COST_MAP = {1: 5.20, 2.5: 8.40, 5: 11.90, 10: 18.10, 1000: 29.80}
INTERNATIONAL_SHIPPING_COST = 26
# NOTE: Must echo changes here to Stripe_Abrev_Name_Map
COMMODITY_VALUE_AND_WEIGHT_MAP = {
    "car world needs me shirt": {"price": 2500, "weight": 0},
    "i want to go to car world shirt": {"price": 2500, "weight": 0},
    "save the attendants shirt": {"price": 2500, "weight": 0},
    "magwadi shirt": {"price": 2500, "weight": 0},
    "quuarux gas wars shirt": {"price": 2500, "weight": 0},
    "enter car world shirt": {"price": 2500, "weight": 0},
    "tat pass bracelet": {"price": 6500, "weight": 0},
    "quuarux earrings": {"price": 3000, "weight": 0},
    "car world emblem earrings": {"price": 2500, "weight": 0},
    "william banks devotional candle": {"price": 1200, "weight": 0},
    "attendant pendant": {"price": 2500, "weight": 0},
    "vip pass": {"price": 1200, "weight": 0},
    "car world supper book": {"price": 1000, "weight": 0},
    "car world supper book 10 pack": {"price": 7000, "weight": 0},
    "pamphlet bundle": {"price": 1000, "weight": 0},
    "car world water": {"price": 500, "weight": 0},
    "enter car world poster": {"price": 3000, "weight": 0},
    "the artifact": {"price": 800000, "weight": 0},
    "devotion point": {"price": 100, "weight": 0},
}
# NOTE: Changes to price map must reflect here
# TODO: source from env vars
STRIPE_ABREVIATED_NAME_MAP = {
    # Forward
    "cnm": "car world needs me shirt",
    "icw": "i want to go to car world shirt",
    "sa": "save the attendants shirt",
    "ms": "magwadi shirt",
    "qg": "quuarux gas wars shirt",
    "ec": "enter car world shirt",
    "tp": "tat pass bracelet",
    "qe": "quuarux earrings",
    "ce": "car world emblem earrings",
    "dc": "william banks devotional candle",
    "ap": "attendant pendant",
    "as": "attendant sponsorship",
    "vp": "vip pass",
    "sb": "car world supper book",
    "bk": "car world supper book 10 pack",
    "pb": "pamphlet bundle",
    "w": "car world water",
    "p": "enter car world poster",
    "a": "the artifact",
    "dp": "devotion point",
    # Backward
    "car world needs me shirt": "cnm",
    "i want to go to car world shirt": "icw",
    "save the attendants shirt": "sa",
    "magwadi shirt": "ms",
    "quuarux gas wars shirt": "qg",
    "enter car world shirt": "ec",
    "tat pass bracelet": "tp",
    "quuarux earrings": "qe",
    "car world emblem earrings": "ce",
    "william banks devotional candle": "dc",
    "attendant pendant": "ap",
    "attendant sponsorship": "as",
    "vip pass": "vp",
    "car world supper book": "sb",
    "car world supper book 10 pack": "bk",
    "pamphlet bundle": "pb",
    "car world water": "w",
    "enter car world poster": "p",
    "the artifact": "a",
    "devotion point": "dp",
}


# TODO: Make this into a lambda layer to be used as a common CWLibrary
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

        print(
            f"DEBUG: ExpressionAttributeValues: {expression_attribute_values}\nUpdateExpression: {update_expression}"
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
        return self.client.get_item(TableName=table_name, Key=key_expression)["Item"]

    # NOTE: This only works for 1mb of data atm (need to add logic for pagination)
    def get_all(self, table_name):
        return self.client.scan(TableName=table_name)["Items"]

    def create(
        self,
        table_name,
        key_expression,
        field_value_map,
        manual_expression_attribute_map=None,
    ):
        # TODO: Roll this block into #format_update_expression_attribute_values
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

    # TODO
    def delete(self, table_name, field_value_map, manual_expression_attribute_map=None):
        """"""

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
        if operation == "update":
            field_name = ":" + field_name

        dynamoType = self.determine_dynamo_data_type(field_value)

        return {
            field_name: {
                dynamoType: (
                    str(field_value)
                    if isinstance(field_value, int) or isinstance(field_value, float)
                    else field_value
                )
            }
        }

    def determine_dynamo_data_type(self, value):
        if isinstance(value, str):
            return "S"
        elif isinstance(value, bool):
            return "BOOL"
        elif isinstance(value, int) or isinstance(value, float):
            return "N"
        # TODO: Add better Map support - this only works for empty maps
        elif isinstance(value, dict):
            # raise Exception(
            #     'Dynamo Map type ("M") is not currently supported - use manual_expression_attribute_map'
            # )
            return "M"
        # NOTE:
        # We don't support mixed-type lists. Make use
        # of manual_expression_attribute_map if you need that.
        elif isinstance(value, list):
            return "SS" if isinstance(value[0], str) else "NS"
        raise Exception(
            f"CWDynamo Client Error: Unhandled data type provided for value: {value}"
        )

    # Example:
    #   {"N": "991"}, {"S": "art"}, etc
    def unformat_dynamo_value_mapping(self, dynamo_value_mapping):
        dynamo_data_type = next(iter(dynamo_value_mapping.keys()))
        value = next(iter(dynamo_value_mapping.values()))

        if dynamo_data_type == "S":
            return value
        if dynamo_data_type == "N":
            value = float(value)
            return int(value) if value.is_integer() else value
        if dynamo_data_type == "BOOL":
            return bool(value)
        # TODO: Implement
        if dynamo_data_type == "M":
            raise Exception(
                "CWDynamo Client Error: Unpacking of SS type not yet supported"
            )
        # TODO: Implement
        if dynamo_data_type == "SS":
            raise Exception(
                "CWDynamo Client Error: Unpacking of SS type not yet supported"
            )

        # Data type doesn't match an expected value
        raise Exception(
            f"CWDynamo Client Error: Unhandled data type provided: value/type - {value}/{dynamo_data_type}"
        )

    def format_update_expression(self, field_name_list):
        update_expression = f"SET {field_name_list[0]} = :{field_name_list[0]}"
        field_name_list.remove(field_name_list[0])

        for field_name in field_name_list:
            update_expression = update_expression + f", {field_name} = :{field_name}"

        return update_expression


class UserTypeEnum(Enum):
    GUEST = 1
    STANDARD = 2
    ADMIN = 3


class CWUser:
    def __init__(self, id, ddp=0, user_type_enum=UserTypeEnum.STANDARD, db_client=None):
        self.id = id
        self.ddp = ddp
        self.user_type_enum = user_type_enum

    def set_email(self, email):
        self.email = email

    def is_guest(self):
        return self.user_type_enum == UserTypeEnum.GUEST

    def increment_ddp_db(self, dynamo_client, ddp=1):
        new_ddp = self.ddp + ddp
        cw_user_table_key_expr = {"id": {"S": self.id}}
        updated_cw_user = dynamo_client.update(
            table_name=USER_TABLE_NAME,
            key_expression=cw_user_table_key_expr,
            field_value_map={"ddp": new_ddp},
        )
        self.ddp += ddp

    @staticmethod
    def from_user_id(id):
        return CWUser(id=id)

    def db_fetch_by_id(self, id, db_client):
        dynamo_client.get(USER_TABLE_NAME, {"id": {"S": id}})

    @staticmethod
    def from_guest_default():
        return CWUser(id="guest", user_type_enum=UserTypeEnum.GUEST)


class DenominationEnum(Enum):
    DOLLAR = 1
    CENT = 2


class CWCost:
    def __init__(self, amt, denomination=DenominationEnum.CENT):
        if denomination == DenominationEnum.DOLLAR:
            self._amt_cents = int(amt * 100)
        else:
            self._amt_cents = int(amt)

    def __str__(self):
        return f"${self.as_dollars()}"

    def __add__(self, x):
        self._amt_cents += x.as_cents()
        return self

    def __iadd__(self, other):
        self._amt_cents += other.as_cents()
        return self

    def as_dollars(self):
        return self._amt_cents / 100

    @staticmethod
    def from_dollars(dollars):
        cent_value = dollars * 100
        return CWCost(cent_value)

    def as_cents(self):
        return int(self._amt_cents)


class CWShippingDetails:
    def __init__(
        self, client_name, city, country, line1, line2, postal_code, state, phone
    ):
        self.client_name = client_name
        self.city = city
        self.country = country
        self.line1 = line1
        self.line2 = line2
        self.postal_code = postal_code
        self.state = state
        self.phone = phone

    @staticmethod
    def from_stripe_event(stripe_shipping_data)
        # TODO: Validate against actual stripe event data
        return CWShippingDetails(
            stripe_shipping_data["client_name"],
            stripe_shipping_data["city"],
            stripe_shipping_date["country"],
            strip_shipping_data["line1"],
            strip_shipping_data["line2"],
            strip_shipping_data["postal_code"],
            strip_shipping_data["state"],
            strip_shipping_data["phone"]
        )

    def get_dynamo_manual_expression_attribute_map(self):
        return {
            "shipping": {
                "M": {
                    "city": {"S": str(self.city or "")},
                    "country": {"S": str(self.country or "")},
                    "line1": {"S": str(self.line1 or "")},
                    "line2": {"S": str(self.line2 or "")},
                    "postal_code": {"S": str(self.postal_code or "")},
                    "us_state": {"S": str(self.state or "")},
                    "client_name": {"S": str(self.client_name or "")},
                    "phone": {"S": str(self.phone or "")},
                }
            }
        }


class CWTransaction:
    def __init__(self, cart, user, id=None, status=None, shipping_country="USA"):
        # sourced from Stripe PaymentIntent API
        self._tx_id = id  # PK in transactions
        self._client_secret = None  # Frontend Stripe token

        self._shipping_country = shipping_country
        self._shipping_details = None

        self.status = status

        self.cart = cart
        self._cw_cost = self._calculate_total()

        self.user = user

    @staticmethod
    def from_stripe_event(stripe_event):
        # Parse event using Stripe lib
        event = stripe.Event.construct_from(stripe_event, stripe.api_key)
        event_data = event["data"]["object"]

        encoded_cart_str = event_data["metadata"]["cart"]
        cart = CWShoppingCart.from_encoded_str(encoded_cart_str)

        user_id = event_data["metadata"]["usr"]
        user = CWUser.from_user_id(user_id)

        # TODO: Implement this static method
        self._shipping_details = CWShippingDetails.from_stripe_event(
            event_data["shipping"]
        )

        tx_status = event_data["status"]

        transaction_id = event_data["id"]

        transaction = CWTransaction(
            cart=cart, user=user, id=transaction_id, status=tx_status
        )

        amount = int(event_data["amount"])
        if transaction.get_cost().as_cents() != int(amount):
            # TODO: Proper log message, this shouldn't happen
            log.error("")
            transaction._cw_cost = CWCost(amount)

        return transaction

    def get_shipping_details(self):
        return self._shipping_details

    def _set_id(self, id):
        self._tx_id = id

    def _set_client_secret(self, client_secret):
        self._client_secret = client_secret

    def get_id(self):
        return self._tx_id

    def get_client_secret(self):
        return self._client_secret

    def get_cost(self):
        return self._cw_cost

    def set_shipping_country(self, country):
        self._shipping_country = country

    def get_shipping_country(self):
        return self._shipping_country

    # NOTE:
    #   Car World makes use of the Stripe platform soley to act as a payment processor.
    #   In this asynchronous workflow, Car World must initiate with Stripe a "Payment Intent."
    #   This can be thought of as establishing a valid payment session, for x ammount.
    #   Once initiated, Stripe returns a client secret to be used by the client to engage
    #   in a direct communication to Stripe's servers. Results of this communication
    #   are communicated after-the-fact to Car World via our own subscription to processed
    #   payment events emitted by Stripe.
    def create_stripe_payment_intent(self):
        # NOTE: Encode Cart contents
        #   The Stripe metadata is limited in its allowed size.
        #   To allow for varied and large orders, we do a manual "shortening" of the cart,
        #   creating a string less suited for human-reading but better for transport.
        encoded_cart_string = self.cart.get_as_encoded_str()

        stripe_payment_intent = stripe.PaymentIntent.create(
            amount=self._cw_cost.as_cents(),
            currency="usd",
            automatic_payment_methods={"enabled": True},
            metadata={"cart": encoded_cart_string, "usr": self.user.id},
        )

        transaction_id = stripe_payment_intent["id"]
        self._set_id(transaction_id)

        client_secret = stripe_payment_intent["client_secret"]
        self._set_client_secret(client_secret)

    def write_to_db(self, db_client):
        db_client.put_item(
            TableName=TRANSACTION_TABLE_NAME,
            Item={
                "id": {"S": self.get_id()},
                "shipping": {
                    "M": {
                        "city": {"S": self.get_shipping_details().city or ""},
                        "country": {"S": self.get_shipping_details().country or ""},
                        "line1": {"S": self.get_shipping_details().line1 or ""},
                        "line2": {"S": self.get_shipping_details().line2 or ""},
                        "postal_code": {"S": self.get_shipping_details().postal_code or ""},
                        "us_state": {"S": self.get_shipping_details().state or ""},
                        "client_name": {"S": self.get_shipping_details().client_name or ""},
                        "phone": {"S": self.get_shipping_details().phone or ""},
                    },
                },
                "tx_status": {"S": self.status},
                "amount": {"N": str(self.get_cost().as_cents())},
                "customer": {"S": self.get_shipping_details().client_name},
                "email": {"S": self.user.email},
                "commodity_list": {"SS": self.cart.get_dynamo_commodity_list()},
                "user_id": {"S": self.user.id},
            },
        )

        return

    # TODO: For logging
    def get_as_dict(self):
        return {}

    def _calculate_total(self):
        total = CWCost(amt=0)
        total += self._calculate_shipping_cost()
        total += self.cart.get_cost()
        return total

    def _calculate_shipping_cost(self):
        shipping_weight = self.cart.get_weight()

        in_order_shipping_weights = sorted(SHIPPING_WEIGHT_COST_MAP.keys())
        shipping_cost = CWCost(amt=0)
        for weight in in_order_shipping_weights:
            if shipping_weight < weight:
                shipping_cost += CWCost.from_dollars(SHIPPING_WEIGHT_COST_MAP[weight])
            else:
                break

        if self._shipping_country != "USA":
            shipping_cost += INTERNATIONAL_SHIPPING_COST
        return shipping_cost


# TODO: Deprecate this, replace with enum
COMMODITY_TYPE_MAP = {
    0: "ticket",
    1: "clothing",
    2: "art",
}


class CommodityTypeEnum(Enum):
    TICKET = 0
    CLOTHING = 1
    ART = 2


# TODO: Finish commodity type stuff
class CWCommodity:
    def __init__(self, name, commodity_type_enum, size=None):
        self.name = name

        cent_value = COMMODITY_VALUE_AND_WEIGHT_MAP[name]["price"]
        self._cw_cost = CWCost(cent_value)

        self.weight = COMMODITY_VALUE_AND_WEIGHT_MAP[name]["weight"]

        self.commodity_type_enum = commodity_type_enum

        if size:
            self.size = size

    def __str__(self):
        return self.name

    def set_size(self, size):
        self.size = size

    def get_cost(self):
        return self._cw_cost

    # TODO: For logging
    def get_as_dict(self):
        return {}

    @staticmethod
    def from_frontend_dict(frontend_dict):
        type = int(frontend_dict["type"])
        commodity_type_enum = CommodityTypeEnum(type)
        if commodity_type_enum == CommodityTypeEnum.CLOTHING:
            commodity = CWCommodity(
                name=frontend_dict["server_name"],
                commodity_type_enum=commodity_type_enum,
                size=frontend_dict["size"],
            )
        else:
            commodity = CWCommodity(
                name=frontend_dict["server_name"],
                commodity_type_enum=commodity_type_enum,
            )
        return commodity

    def get_weight(self):
        return self.weight


class CWShoppingCartEntry:
    def __init__(self, commodity, quantity):
        self.commodity = commodity
        self.quantity = quantity
        self._cw_cost = self._calculate_cost()
        self.weight = self._calculate_weight()

    def get_cost(self):
        return self._cw_cost

    def get_weight(self):
        return self.weight

    def _calculate_cost(self):
        cost_cents = self.commodity.get_cost().as_cents() * self.quantity
        return CWCost(amt=cost_cents)

    def _calculate_weight(self):
        weight = self.commodity.get_weight() * self.quantity
        return weight

    # TODO: For logging
    def get_as_dict(self):
        return {}


class CWShoppingCart:
    def __init__(self, shopping_cart_entry_list):
        self.shopping_cart_entry_list = shopping_cart_entry_list
        self._cw_cost, self._size = self._calculate_cost_and_size()
        self._weight = self._calculate_weight()

    def get_cost(self):
        return self._cw_cost

    def _calculate_cost_and_size(self):
        cw_cost = CWCost(amt=0)
        size = 0
        for shopping_cart_entry in self.shopping_cart_entry_list:
            # NOTE: This syntax is fine since we overrode CWCost::__add__
            cw_cost += shopping_cart_entry.get_cost()
            size += shopping_cart_entry.quantity
        return cw_cost, size

    def get_size(self):
        return self._size

    def get_weight(self):
        return self._weight

    def _calculate_weight(self):
        weight = 0
        for shopping_cart_entry in self.shopping_cart_entry_list:
            weight += shopping_cart_entry.get_weight()
        return weight

    @staticmethod
    def from_frontend_dict(frontend_cart_dict):
        try:
            shopping_cart_entry_list = []
            for commodity_dict in frontend_cart_dict:
                commodity = CWCommodity.from_frontend_dict(commodity_dict)
                quantity = commodity_dict["quantity"]

                cart_entry = CWShoppingCartEntry(commodity=commodity, quantity=quantity)
                shopping_cart_entry_list.append(cart_entry)
        except Exception as e:
            print(e)
            raise e
        return CWShoppingCart(shopping_cart_entry_list=shopping_cart_entry_list)

    # TODO: For logging
    def get_as_dict(self):
        return {}

    #   This method takes this directly-translated map to string:
    #     [{'server_name': 'magwadi shirt', 'quantity': 1, 'type': 1, 'size': 'l'}, {'server_name': 'quuarux earrings', 'quantity': 2, 'type': 2}]
    #   and concatenates it to this:
    #     1_ms_1_l*2_qe_2
    def get_as_encoded_str(self):
        encoded_string = ""
        for index, cart_entry in enumerate(self.shopping_cart_entry_list):
            if not index == 0:
                encoded_string += "*"

            comm_type_value = cart_entry.commodity.commodity_type_enum.value
            encoded_string += f"{comm_type_value}_{STRIPE_ABREVIATED_NAME_MAP[cart_entry.commodity.name]}_{cart_entry.quantity}"

            if cart_entry.commodity.commodity_type_enum == CommodityTypeEnum.CLOTHING:
                encoded_string += f"_{cart_entry.commodity.size}"
        return encoded_string

    def get_dynamo_commodity_list(self):
        commodity_list = []
        for shopping_cart_entry in self.shopping_cart_entry_list:
            # prefix quantity as dynamo SS does not allow duplicate entries
            formatted_commodity_name = str(shopping_cart_entry.quantity) + "_" +  shopping_cart_entry.commodity.name

            # postfix size if applicable
            if shopping_cart_entry.commodity.commodity_type_enum == CommodityTypeEnum.CLOTHING:
                size = shopping_cart_entry.commodity.size
                formatted_commodity_name = formatted_commodity_name + "_" + size

            commodity_list.append(formatted_commodity_name)

        return commodity_list



    @staticmethod
    def from_encoded_str(encoded_str):
        shopping_cart_entry_list = []
        commodity_list = encoded_str.split("*")
        for commodity in commodity_list:
            # Process shortened commodity string
            commodity_props = commodity.split("_")
            type = int(commodity_props[0])
            abreviated_name = commodity_props[1]
            quantity = int(commodity_props[2])

            # Assign standard cart format
            server_name = STRIPE_ABREVIATED_NAME_MAP[abreviated_name]

            if CommodityTypeEnum(type) == CommodityTypeEnum.CLOTHING:
                size = commodity_props[3]
                entry = CWShoppingCartEntry(
                    CWCommodity(server_name, type, size), quantity
                )
            else:
                entry = CWShoppingCartEntry(CWCommodity(server_name, type), quantity)

            shopping_cart_entry_list.append(entry)
        return cart


####################################################################################################################################################################################
##                                                                                                                                                                                ##
####################################################################################################################################################################################


def get_commodity_list(dynamo_client):
    try:
        # Retrieve backend list of commodities
        commodities = dynamo_client.get_all(COMMODITY_TABLE_NAME)
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(f"SERVER_ERROR: Failed to obtain Commodites from DB -- {error}")
        return {
            "code": 500,
            "message": "SERVER_ERROR: Failed to obtain Commodites from DB",
            "error": error,
        }

    try:
        # Format commodities for FE
        fe_commodity_map = fe_commodity_map_from_dynamo_list(commodities, dynamo_client)
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(
            f"SERVER_ERROR: Failed to convert Dynamo commodity list to FE Mapping -- {error}"
        )
        return {
            "code": 500,
            "message": "SERVER_ERROR: Failed to convert Dynamo commodity list to FE Mapping",
            "error": error,
        }

    return {
        "code": 200,
        "message": "Successfully retreived commodity list",
        "body": {"commodity_list": fe_commodity_map},
    }


def fe_commodity_map_from_dynamo_list(dynamo_commodity_list, dynamo_client):
    fe_commodity_map = {}
    for commodity in dynamo_commodity_list:
        # Convert Dynamo values mappings to raw values
        commodity["quantity"] = dynamo_client.unformat_dynamo_value_mapping(
            commodity["quantity"]
        )
        commodity["product_name"] = dynamo_client.unformat_dynamo_value_mapping(
            commodity["product_name"]
        )
        commodity["product_type"] = dynamo_client.unformat_dynamo_value_mapping(
            commodity["product_type"]
        )

        # Dynamo stores each size of clothing separately.
        # Consequently, we must make sure to capture the quantity of all
        # of these different sizes, and aggregate them.
        if commodity["product_type"] == "clothing":
            name_and_size_array = commodity["product_name"].split("_")
            commodity_name = name_and_size_array[0]
            commodity_size = name_and_size_array[1]

            # If we have already added this commodity to the map,
            # merely update with the quantity of this new size.
            if commodity_name in fe_commodity_map:
                fe_commodity_map[commodity_name]["quantity"].update(
                    {commodity_size: commodity["quantity"]}
                )
            # If we have yet to add this commodity to the map,
            # add the commodity with a format that allows for the other sizes.
            else:
                fe_commodity_map.update(
                    {
                        commodity_name: {
                            "quantity": {commodity_size: commodity["quantity"]},
                            "commodityType": commodity["product_type"],
                        }
                    }
                )
        else:
            fe_commodity_map.update(
                {
                    commodity["product_name"]: {
                        "quantity": commodity["quantity"],
                        "commodityType": commodity["product_type"],
                    },
                }
            )
    return fe_commodity_map


def update_transaction(update_transaction_body, dynamo_client):
    # validate body
    try:
        transaction_record_id = update_transaction_body["transaction_record_id"]
        status = update_transaction_body["tx_status"]
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(
            f"CLIENT_ERROR: incorrect payload submitted to CWCC /update_transaction: {update_transaction_body} | {error}"
        )
        return {
            "code": 400,
            "message": f"CLIENT_ERROR: incorrect payload submitted to CWCC /update_transaction: {update_transaction_body}",
            "error": error,
        }

    try:
        transaction_record = update_transaction_record_client_call(
            transaction_record_id, status, dynamo_client
        )
        return {
            "code": 200,
            "message": "updated transaction_record",
        }
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(f"SERVER_ERROR: failed to update transaction_record | {error}")
        return {
            "code": 500,
            "message": "SERVER_ERROR: failed to update transaction_record",
            "error": error,
        }


# TODO: https://docs.powertools.aws.dev/lambda/python/2.5.0/utilities/idempotency/#lambda-timeout-sequence-diagram
#       Idempotency - why? The moron that wrote the frontend (it was me, I did it) can't
#       seem to keep the client from spamming a few of these unintentionally.
# @idempotent_function(
#    data_keyword_argument="order", config=config, persistence_store=dynamodb
# )
def create_payment_intent(create_payment_intent_body, user_id, dynamo_client):
    log.info("Initiating create_payment_intent...")

    user = CWUser(id=user_id)

    try:
        cart = CWShoppingCart.from_frontend_dict(create_payment_intent_body["cart"])
    except Exception as e:
        incorrect_payload_error = f"CLIENT_ERROR: incorrect payload submitted to CWCC /secret: got {create_payment_intent_body}, expected cart of commodities"
        log.exception(incorrect_payload_error)
        return {
            "code": 400,
            "message": incorrect_payload_error,
            "error": {
                "message": str(e),
                "stack": traceback.format_exc(),
            },
        }

    transaction = CWTransaction(cart=cart, user=user)

    try:
        transaction.create_stripe_payment_intent()
        log.info(
            "Successfully generated stripe PaymentIntent",
            transaction_id=transaction.get_id(),
            user_id=user_id,
        )
    except Exception as e:
        stripe_api_failure = "SERVER_ERROR: Failed to initiate Stripe Payment Intent"
        log.exception(stripe_api_failure, user_id=user_id)
        return {
            "code": 500,
            "message": stripe_api_failure,
            "error": {
                "message": str(e),
                "stack": traceback.format_exc(),
            },
        }

    return {
        "code": 200,
        "message": "Succesfully created Stripe PaymentIntent",
        "body": {
            "client_secret": transaction.get_client_secret(),
            "stripe_payment_intent_id": transaction.get_id(),
        },
    }


def update_transaction_record_client_call(transaction_id, status, dynamo_client):
    response = dynamo_client.update(
        table_name=TRANSACTION_TABLE_NAME,
        key_expression={"id": {"S": transaction_id}},
        field_value_map={"tx_status": status},
    )
    return response


def update_transaction_record_webhook_call(
    transaction_id, name, shipping, status, stripe_transaction_id, dynamo_client
):
    response = dynamo_client.update(
        table_name=TRANSACTION_TABLE_NAME,
        key_expression={"id": {"S": transaction_id}},
        field_value_map={
            "tx_status": status,
            "client_name": str(name or ""),
            "stripe_transaction_id": stripe_transaction_id,
        },
        manual_expression_attribute_map={
            "shipping": {
                "M": {
                    "city": {"S": str(shipping["address"]["city"] or "")},
                    "country": {"S": str(shipping["address"]["country"] or "")},
                    "line1": {"S": str(shipping["address"]["line1"] or "")},
                    "line2": {"S": str(shipping["address"]["line2"] or "")},
                    "postal_code": {"S": str(shipping["address"]["postal_code"] or "")},
                    "us_state": {"S": str(shipping["address"]["state"] or "")},
                    "client_name": {"S": str(shipping["name"] or "")},
                    "phone": {"S": str(shipping["phone"] or "")},
                }
            }
        },
    )

    return response


def handle_webhook(stripe_event, dynamo_client):
    try:
        # TODO: Impl
        # This doesn't work since we have transitioned to class-based calls,
        # as the underyling dependency on CWShippingDetails has not implemented
        # the static method CWShippingDetails.from_stripe_event
        transaction = CWTransaction.from_stripe_event(stripe_event)
    except Exception as e:
        stripe_webhook_parse_failure = (
            "SERVER_ERROR: Failed to parse Stripe webhook event"
        )
        log.exception(
            stripe_webhook_parse_failure,
            stripe_event=stripe_event,
        )
        return {
            "code": 500,
            "message": stripe_webhook_parse_failure,
            "error": {"message": str(e), "stack": traceback.format_exc()},
        }

    if transaction.user.is_guest():
        # Obtain email from cache for guest user
        try:
            email = obtain_email_from_cache(key=transaction.get_id())
            transaction.user.set_email(email)
        except Exception as e:
            user_email_s3_lookup_failure = (
                "SERVER_ERROR: failed to obtain email from user record or s3 cache"
            )
            log.exception(user_email_s3_lookup_failure)
            return {
                "code": 500,
                "message": user_email_s3_lookup_failure,
                "error": {
                    "message": str(e),
                    "stack": traceback.format_exc(),
                },
            }

    try:
        transaction.write_to_db(dynamo_client)
    except Exception as e:
        tx_db_write_failure = "Failed to write transaction_record to db"
        log.exception(tx_db_write_failure)
        return {
            "code": 500,
            "message": tx_db_write_failure,
            "error": {
                "message": str(e),
                "stack": traceback.format_exc(),
            },
        }

    # Increment DDP for purchases made by registered users
    if not transaction.user.is_guest():
        try:
            # TODO: Implement
            transaction.user.increment_ddp_db(
                dynamo_client, ddp=transaction.cart.size()
            )
        except Exception as e:
            # TODO: Queue DynamoDB-Error Retries
            # Can look at old commits to find the skeleton for this.
            # For now, just logging.
            #
            # While we're here...
            # it would probably be easier to just create a MetricFilter(1)
            # and MetricAlarm(2) that listen for these logs and notify SNS.
            # Point SES at the SNS, recieve alert. Maybe expensive though?
            #
            # 1: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/MonitoringLogData.html
            # 2: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html
            #
            log_context = {
                "user_id": transaction.user.id,
                "transaction_id": transaction.get_id(),
            }
            log.exception("SERVER_ERROR: Failed to update ddp for user", **log_context)

    # Send an email to William, Russell, and Customer about completed purchase
    try:
        # TODO
        SESService.send_email_order_details_to_admins(transaction=transaction)
        SESService.send_email_order_details_to_customer(transaction=transaction)

        return {"code": 200}
    except Exception as e:
        ses_email_send_error = "SERVER_ERROR: failed to email about commodity purchase"
        log.exception(ses_email_send_error)
        return {
            "code": 500,
            "message": ses_email_send_error,
            "error": {
                "message": str(e),
                "stack": traceback.format_exc(),
            },
        }


def cache_email_action(cache_email_body):
    try:
        email = cache_email_body["email"]
        if type(email) != str or len(email) < 6 or len(email) > 84 or " " in email:
            raise Exception("Email failed to validate")

        transaction_id = cache_email_body["transaction_id"]
        if type(transaction_id) != str or " " in transaction_id:
            raise Exception("Transaction ID failed to validate")

        write_to_email_cache(key=transaction_id, email=email)
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(f"SERVER_ERROR: failed to cache email | {error}")
        return {
            "code": 500,
            "message": "SERVER_ERROR: failed to cache email",
            "error": error,
        }

    return {"code": 200, "message": "success"}


def obtain_email_from_cache(key):
    email_item = S3_CLIENT.get_object(Bucket=TRANSACTION_EMAIL_CACHE_NAME, Key=key)
    email = email_item["Body"].read().decode("utf-8")

    return email


def write_to_email_cache(key, email):
    S3_CLIENT.put_object(
        Bucket=TRANSACTION_EMAIL_CACHE_NAME, Key=key, Body=email.encode("utf-8")
    )


# NOTE:
#   See cw_cart_from_short_string() for explanation of formatting
def determine_item_count_from_cart(commodity_list):
    # Count items in transaction
    item_count = 0
    for commodity in commodity_list:
        commodity_count = int(commodity.split("_")[0])
        item_count += commodity_count
    return item_count


def grantDdpToUser(cw_user_record, commodity_list, item_count, dynamo_client):
    current_ddp = int(cw_user_record["ddp"]["N"])
    new_ddp = current_ddp + item_count

    # Update user with new DDP count
    cw_user_table_key_expr = {"id": {"S": cw_user_record["id"]["S"]}}
    try:
        updated_cw_user = dynamo_client.update(
            table_name=USER_TABLE_NAME,
            key_expression=cw_user_table_key_expr,
            field_value_map={"ddp": new_ddp},
        )
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(
            f'SERVER_ERROR: Failed to update ddp for user:{cw_user_record["id"]["S"]} | {error}'
        )

        # NOTE: Queue DynamoDB-Error Retries
        queue_cw_db_retry_lambda(
            controller="commerce",
            action="grant_ddp",
            db_actions=[
                {
                    "operation": "update",
                    "table_name": "users",
                    "key_expression": cw_user_table_key_expr,
                    "field_value_map": {"ddp": new_ddp},
                },
                {
                    "operation": "update",
                    "table_name": "commodities",
                    "key_expression": {"product_name": {"S": product_name}},
                    "field_value_map": {"quantity": new_quantity},
                },
            ],
        )

    return


def remove_purchased_commodities_from_stock(commodity_list, dynamo_client):
    for purchased_commodity in commodity_list:
        # NOTE: Format is quantity_commodity
        quantity_purchased = purchased_commodity.split("_", 1)[0]
        product_name = purchased_commodity.split("_", 1)[1]

        try:
            old_quantity = dynamo_client.get(
                table_name=COMMODITY_TABLE_NAME,
                key_expression={"product_name": {"S": product_name}},
            )["quantity"]["N"]
            new_quantity = int(old_quantity) - int(quantity_purchased)

            print(
                f"DEBUG - old quantity: {old_quantity} | new_quantity: {new_quantity}"
            )

            dynamo_client.update(
                table_name=COMMODITY_TABLE_NAME,
                key_expression={"product_name": {"S": product_name}},
                field_value_map={"quantity": new_quantity},
            )
        except Exception as e:
            error = {
                "message": str(e),
                "stack": traceback.format_exc(),
            }
            print(
                f"SERVER_ERROR: Failed to update quantity of {product_name} record | {error}"
            )

            # TODO: Queue DynamoDB-Error Retries
            # queue_cw_db_retry_lambda(
            #     controller="commerce",
            #     action="remove_commodity",
            #     db_actions=[
            #         {
            #             "operation": "get",
            #             "table_name": "commodities",
            #             "key_expression": {"product_name": {"S": product_name}},
            #         },
            #         {
            #             "operation": "update",
            #             "table_name": "commodities",
            #             "key_expression": {"product_name": {"S": product_name}},
            #             "field_value_map": {"quantity": new_quantity},
            #         },
            #     ],
            # )


def send_email_order_details_to_customer(
    shipping,
    customer_name,
    customer_email,
    products,
    amt_in_cents,
    item_count,
    is_guest_purchase,
):
    if is_guest_purchase:
        cw_user_string = f"""
        <p>
            Thanks again for your support! Have you considered
            <a href="https://carworld.love/car_world_nation">
                becoming a Member of Car World Nation
            </a>?
        </p>
        """
    else:
        cw_user_string = f"""
        <p>
            As a reward for your purchase, we have gone ahead and added {item_count} DDP to your account!
        </p>
        """

    product_table = cw_email_product_table(products)
    customer_shipping = cw_email_format_shipping(shipping, customer_email)
    dollar_cost = "%0.2f" % (amt_in_cents / 100)
    body_html = f"""
    <html>
        <head></head>
        <body>
        <h1>carworld.love: Order Confirmation</h1>
        <hr/>
        <p>
            Congratulations, { customer_name }, on a successful order from carworld.love!
        </p>
        <p>
            { product_table }
        </p>
        <p>
            Your purchase in the amount of ${ dollar_cost } has been processed.
            William Banks himself will soon be hard at work preparing your item(s)
            to be sent to the following location:
        </p>
        { customer_shipping }
        { cw_user_string }
        <p>
            For any questions or concerns in relation to your order, contact William
            Banks directly at: williambanks500@gmail.com. Please do not responded to
            this email (merch@carworld.love); responses are not being recorded and
            will not be seen.
        </p>
        </body>
    </html>
                    """

    email_message = {
        "Body": {
            "Html": {
                "Charset": "utf-8",
                "Data": body_html,
            },
        },
        "Subject": {
            "Charset": "utf-8",
            "Data": "New Order placed on carworld.love!",
        },
    }

    ses_response = SES_CLIENT.send_email(
        Destination={"ToAddresses": [customer_email]},
        Message=email_message,
        Source=SES_SENDER_EMAIL,
        ConfigurationSetName=SES_CONFIG_ID,
    )

    return f"ses response id: {ses_response['MessageId']} | ses success code: {ses_response['ResponseMetadata']['HTTPStatusCode']}."


def send_email_order_details_to_admins(
    shipping,
    customer_name,
    customer_email,
    products,
    amt_in_cents,
    username,
    is_guest_purchase,
):
    if is_guest_purchase:
        cw_user_string = f"{customer_name} is a guest user."
    else:
        cw_user_string = (
            f"{customer_name} is a user of carworld.love with the username: {username}."
        )

    product_table = cw_email_product_table(products)
    customer_shipping = cw_email_format_shipping(shipping, customer_email)
    dollar_cost = "%0.2f" % (amt_in_cents / 100)
    body_html = f"""
    <html>
        <head></head>
        <body>
        <h1>carworld.love: New Order Placed</h1>
        <hr/>
        <p>
            An order in the amount of ${dollar_cost} has been placed by {customer_name}!
        </p>
        <p>
            { cw_user_string }
        </p>
        {product_table}
        {customer_shipping}
        </body>
    </html>
                    """

    email_message = {
        "Body": {
            "Html": {
                "Charset": "utf-8",
                "Data": body_html,
            },
        },
        "Subject": {
            "Charset": "utf-8",
            "Data": "New Order placed on carworld.love!",
        },
    }

    ses_response = SES_CLIENT.send_email(
        Destination={"ToAddresses": SES_ADMIN_LIST},
        Message=email_message,
        Source=SES_SENDER_EMAIL,
        ConfigurationSetName=SES_CONFIG_ID,
    )

    return f"ses response id: {ses_response['MessageId']} | ses success code: {ses_response['ResponseMetadata']['HTTPStatusCode']}."


def cw_email_product_table(products):
    cw_email_product_table_entries = cw_email_obtain_products_as_td(products)

    table_html = f"""
        <table>
            <tr>
                <th>Quantity</th>
                <th>Size</th>
                <th>Product</th>
            </tr>
            {cw_email_product_table_entries}
        </table>
    """

    return table_html


def cw_email_obtain_products_as_td(products):
    cw_email_product_table_entries = ""
    for product in products:
        product_details = product.split("_")

        quantity = product_details[0]
        product_name = product_details[1]
        # size, if applicable
        size = product_details[2].upper() if len(product_details) == 3 else ""

        cw_email_product_table_entries += f"""
          <tr>
            <td>{quantity}</td>
            <td>{size}</td>
            <td>{product_name}</td>
          </tr>
        """

    return cw_email_product_table_entries


def cw_email_format_shipping(shipping, customer_email):
    shipping_html = f"""
      <p>
        {customer_email}
        <br/>
        {shipping["name"]}
        <br/>
        {shipping["address"]["line1"]}
        <br/>
        {shipping["address"]["line2"]}
        <br/>
        {shipping["address"]["city"]}, {shipping["address"]["state"]} {shipping["address"]["postal_code"]}
        <br/>
        {shipping["address"]["country"]}
        <br/>
        {shipping["phone"]}
      </p>
    """

    return shipping_html


# TODO: Queues a retry of a particular db write for the CWRetryDatabaseActionLambda
def queue_cw_db_retry_lambda(controller, action, db_actions):
    """"""


########################################################
# Controller Action Handler
########################################################
CW_DYNAMO_CLIENT = CWDynamoClient()


# https://docs.powertools.aws.dev/lambda/python/latest/core/log/#built-in-correlation-id-expressions
@log.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_HTTP, log_event=True
)
def handler(event, context):
    # Parse request
    try:
        request = {
            "type": event["requestContext"]["http"]["method"],
            "action": event["rawPath"].replace("/commerce/", ""),
        }
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(
            f"SERVER_ERROR: Failed to parse event into request format: {event} | Encountered error -- {error}"
        )
        return {
            "code": 500,
            "message": f"SERVER_ERROR: Failed to parse event into request format: {event}",
            "error": error,
        }

    # Add endpoint action to log
    log.append_keys(action=request["action"])

    # Direct to proper controller action
    try:
        if request["action"] == "secret":
            # Given that this is a protected action, the JWT provided in the header
            # has already been parsed, with the UserID being provided in the reqContext
            user_id = event["requestContext"]["authorizer"]["lambda"]["user_id"]
            log.append_keys(user_id=user_id)

            # /secret has a request body
            request["body"] = json.loads(event["body"])

            # Create PaymentIntent
            res = create_payment_intent(
                create_payment_intent_body=request["body"],
                user_id=user_id,
                dynamo_client=CW_DYNAMO_CLIENT,
            )
        elif request["action"] == "cache_email":
            # /cache_email has a request body
            request["body"] = json.loads(event["body"])

            res = cache_email_action(cache_email_body=request["body"])
        elif request["action"] == "webhook":
            # /webhook has a request body
            request["body"] = json.loads(event["body"])

            res = handle_webhook(
                stripe_event=request["body"], dynamo_client=CW_DYNAMO_CLIENT
            )
        elif request["action"] == "commodities":
            res = get_commodity_list(dynamo_client=CW_DYNAMO_CLIENT)
        else:
            raise Exception(f'Invalid route: {request["action"]}')
    except Exception as e:
        unhandled_exception = "SERVER_ERROR: Unhandled server error encountered"
        log.exception(unhandled_exception)
        return {
            "code": 500,
            "message": unhandled_exception,
            "error": {
                "message": str(e),
                "stack": traceback.format_exc(),
            },
        }

    # Add headers for CORS
    res["headers"] = {
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    }

    return res
