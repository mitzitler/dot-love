# TODO: Implement (or make use of pre-existing) propper logger, replace #print statements
# TODO: Move resource initialization out of child processes of Handler!
#       Initializing object outside of handler allows their re-use in succesive
#       lambda calls, and shortens the execution time (which is what is actually billed)

import os
import json
import traceback
import stripe
import boto3
import hashlib

# Environment Variables
SES_CONFIG_ID = os.environ["ses_config_id"]
USER_TABLE_NAME = os.environ["user_table_name"]
COMMODITY_TABLE_NAME = os.environ["commodity_table_name"]
TRANSACTION_TABLE_NAME = os.environ["transaction_table_name"]
TRANSACTION_EMAIL_CACHE_NAME = os.environ["transaction_email_cache_s3_name"]
stripe.api_key = os.environ["stripe_secret"]

# Clients
S3_CLIENT = boto3.resource("s3")

# TODO: move these mapping to param store, shouldn't be hardcoded here
# Constants
EMAIL_RECIPIENTS = [
    "themattsaucedo@gmail.com",
    # TODO: uncomment for site-launch
    # "williambanks500@gmail.com",
    # "rkats0524@gmail.com",
]
SES_SENDER_EMAIL = "themattsaucedo@gmail.com"
# NOTE: Must echo changes here to Stripe_Abrev_Name_Map
COMMODITY_VALUE_MAP = {
    "save the attendants shirt": 2500,
    "magwadi shirt": 2500,
    "quuarux gas wars shirt": 2500,
    "enter car world shirt": 2500,
    "tat pass bracelet": 6500,
    "quuarux earrings": 3000,
    "car world emblem earrings": 2500,
    "william banks devotional candle": 1200,
    "attendant pendant": 2500,
    "vip pass": 1200,
    "car world supper book": 1000,
    "car world supper book 10 pack": 7000,
    "pamphlet bundle": 1000,
    "car world water": 500,
    "enter car world poster": 3000,
    "the artifact": 800000,
    "devotion point": 100,
}
# NOTE: Changes to price map must reflect here
STRIPE_ABREVIATED_NAME_MAP = {
    # Forward
    "sa": "save the attendants shirt",
    "ms": "magwadi shirt",
    "qg": "quuarux gas wars shirt",
    "ec": "enter car world shirt",
    "tp": "tat pass bracelet",
    "qe": "quuarux earrings",
    "ce": "car world emblem earrings",
    "dc": "william banks devotional candle",
    "ap": "attendant pendant",
    "vp": "vip pass",
    "sb": "car world supper book",
    "bk": "car world supper book 10 pack",
    "pb": "pamphlet bundle",
    "w": "car world water",
    "p": "enter car world poster",
    "a": "the artifact",
    "dp": "devotion point",
    # Backward
    "save the attendants shirt": "sa",
    "magwadi shirt": "ms",
    "quuarux gas wars shirt": "qg",
    "enter car world shirt": "ec",
    "tat pass bracelet": "tp",
    "quuarux earrings": "qe",
    "car world emblem earrings": "ce",
    "william banks devotional candle": "dc",
    "attendant pendant": "ap",
    "vip pass": "vp",
    "car world supper book": "sb",
    "car world supper book 10 pack": "bk",
    "pamphlet bundle": "pb",
    "car world water": "w",
    "enter car world poster": "p",
    "the artifact": "a",
    "devotion point": "dp",
}
COMMODITY_TYPE_MAP = {0: "ticket", 1: "clothing", 2: "art"}


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
            dynamo_formatted_value_mapping = dynamo_format_value_mapping(
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
                dynamoType: str(field_value)
                if isinstance(field_value, int) or isinstance(field_value, float)
                else field_value
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
        "body": {"commodityList": fe_commodity_map},
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
            f"CLIENT_ERROR: incorrect payload submitted to CWCC /update_transaction: {create_payment_intent_body} | {error}"
        )
        return {
            "code": 400,
            "message": f"CLIENT_ERROR: incorrect payload submitted to CWCC /update_transaction: {create_payment_intent_body}",
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


def create_payment_intent(create_payment_intent_body, user_id, dynamo_client):
    # Validate cart body
    try:
        cart = create_payment_intent_body["cart"]
        for commodity in cart:
            commodity_name = commodity["server_name"]
            quantity = commodity["quantity"]
            type = int(commodity["type"])

            # Clothing has a size
            if COMMODITY_TYPE_MAP[type] == "clothing":
                size = commodity["size"]
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(
            f"CLIENT_ERROR: incorrect payload submitted to CWCC /secret: got {create_payment_intent_body}, expected cart of commodities | {error}"
        )
        return {
            "code": 400,
            "message": f"CLIENT_ERROR: incorrect payload submitted to CWCC /secret: got {create_payment_intent_body}, expected cart of commodities",
            "error": error,
        }

    # Quantify transaction cost
    try:
        amount = calculate_transaction_amount(cart)
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(f"CLIENT_ERROR: Failed to parse shopping cart: {cart} | {error}")
        return {
            "code": 400,
            "message": f"CLIENT_ERROR: Failed to parse shopping cart: {cart}",
            "error": error,
        }

    # Initiate Payment Intent
    # NOTE:
    #   Car World makes use of the Stripe platform soley to act as a payment processor.
    #   In this asynchronous workflow, Car World must initiate with Stripe a "Payment Intent."
    #   This can be thought of as establishing a valid payment session, for x ammount.
    #   Once initiated, Stripe returns a client secret to be used by the client to engage
    #   in a direct communication to Stripe's servers. Results of this communication
    #   are communicated after-the-fact to Car World via our own subscription to processed
    #   payment events emitted by Stripe.
    try:
        # NOTE: Convert Cart to short string
        #   The Stripe metadata is limited in its allowed size (discovered during testing).
        #   To allow for varied and large orders, we do a manual "shortening" of the cart,
        #   creating a string less suited for human-reading but better for transport.
        #   This method takes this directly-translated map to string:
        #     [{'server_name': 'magwadi shirt', 'quantity': 1, 'type': 1, 'size': 'l'}, {'server_name': 'quuarux earrings', 'quantity': 2, 'type': 2}]
        #   and concatenates it to this:
        #     1_ms_1_l*2_qe_2
        short_cart_string = cw_cart_to_short_string(cart)

        stripe_payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            automatic_payment_methods={"enabled": True},
            metadata={"cart": short_cart_string, "usr": user_id},
        )

        client_secret = stripe_payment_intent["client_secret"]
        transaction_id = stripe_payment_intent["id"]
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(f"SERVER_ERROR: Failed to initiate Stripe Payment Intent | {error}")
        return {
            "code": 500,
            "message": "SERVER_ERROR: Failed to initiate Stripe Payment Intent",
            "error": error,
        }

    return {
        "code": 200,
        "message": "Succesfully created Stripe PaymentIntent",
        "body": {
            "client_secret": client_secret,
            "stripe_payment_intent_id": transaction_id,
        },
    }


def calculate_transaction_amount(cart):
    amount = 0
    for commodity in cart:
        name = commodity["server_name"]
        if name in COMMODITY_VALUE_MAP.keys():
            amount = amount + (COMMODITY_VALUE_MAP[name] * commodity["quantity"])
        else:
            raise Exception(
                f"Invalid commodity name received: {name}, valid names: {COMMODITY_VALUE_MAP.keys()}"
            )
    return amount


# TODO: Replace raw dynamo client call with cw_dynamo_client
def create_transaction_record(
    transaction_id,
    shipping,
    status,
    amount,
    name,
    commodity_list,
    user_id,
    dynamo_client,
):
    dynamo_client = dynamo_client.client

    dynamo_client.put_item(
        TableName=TRANSACTION_TABLE_NAME,
        Item={
            "id": {"S": transaction_id},
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
            },
            "tx_status": {"S": status},
            "amount": {"N": str(amount)},
            "customer": {"S": name},
            "commodity_list": {"SS": commodity_list},
            "user_id": {"S": user_id},
        },
    )

    return


def format_commodity_list_from_cart(cart):
    commodity_list = []
    for commodity in cart:
        # prefix quantity as dynamo SS does not allow duplicate entries
        formatted_commodity_name = (
            str(commodity["quantity"]) + "_" + commodity["server_name"]
        )

        # postfix size if applicable
        if COMMODITY_TYPE_MAP[int(commodity["type"])] == "clothing":
            size = commodity["size"]
            formatted_commodity_name = formatted_commodity_name + "_" + size

        commodity_list.append(formatted_commodity_name)

    return commodity_list


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


# Explanation on formatting:
# type_shortName_quantity(_size)...*type_shortName_quantity(_size)
# >>> string = "T_A_x*T_A_x_y*T_A_x"
# >>> string.split("*")
# ['1_sa_1_s', '2_tp_3', '1_ms_2_l']
# >>>
def cw_cart_to_short_string(cart):
    short_string = ""
    for index, commodity in enumerate(cart):
        if not index == 0:
            short_string += "*"

        short_string += f'{commodity["type"]}_{STRIPE_ABREVIATED_NAME_MAP[commodity["server_name"]]}_{commodity["quantity"]}'

        if COMMODITY_TYPE_MAP[commodity["type"]] == "clothing":
            short_string += f'_{commodity["size"]}'
    return short_string


# Explanation on formatting:
# type_shortName_quantity(_size)...*type_shortName_quantity(_size)
# >>> string = "T_A_x*T_A_x_y*T_A_x"
# >>> string.split("*")
# ['1_sa_1_s', '2_tp_3', '1_ms_2_l']
# >>>
def cw_cart_from_short_string(short_string):
    cart = []
    commodity_list = short_string.split("*")
    for commodity in commodity_list:
        # Process shortened commodity string
        commodity_props = commodity.split("_")
        type = int(commodity_props[0])
        abreviated_name = commodity_props[1]
        quantity = int(commodity_props[2])

        # Assign standard cart format
        cart_obj = {
            "type": type,
            "server_name": STRIPE_ABREVIATED_NAME_MAP[abreviated_name],
            "quantity": quantity,
        }

        if COMMODITY_TYPE_MAP[type] == "clothing":
            cart_obj.update({"size": commodity_props[3]})

        cart.append(cart_obj)
    return cart


def handle_webhook(stripe_event, dynamo_client):
    try:
        event = stripe.Event.construct_from(stripe_event, stripe.api_key)
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(
            f"SERVER_ERROR: Failed to parse Stripe webhook event: {stripe_event} | {error}"
        )
        return {
            "code": 500,
            "message": "SERVER_ERROR: Failed to parse Stripe webhook event",
            "error": error,
        }

    try:
        event_data = event["data"]["object"]

        # Obtain data needed to create record of Transaction
        transaction_id = event_data["id"]
        shipping = event_data["shipping"]
        status = event_data["status"]
        amount = event_data["amount"]
        name = event_data["shipping"]["name"]

        # Get dynamo-friendly commodity list
        # NOTE: use of #eval, as the cart dict is stored as a str on Stripe's end
        cart = cw_cart_from_short_string(event_data["metadata"]["cart"])
        commodity_list = format_commodity_list_from_cart(cart)

        # Grab user ID for user followup actions
        user_id = event_data["metadata"]["usr"]
        is_guest_purchase = user_id == "guest"

        print(f"DEBUG - cart metadata: {event_data['metadata']['cart']}")
        print(f"DEBUG - commodity_list: {commodity_list}")
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(
            f"SERVER_ERROR: Failed to parse Transaction data from Stripe callback | {error}"
        )
        return {
            "code": 500,
            "message": "SERVER_ERROR: Failed to parse Transaction data from Stripe callback",
            "error": error,
        }

    cw_user_record = None
    try:
        if not is_guest_purchase:
            cw_user_record = dynamo_client.get(USER_TABLE_NAME, {"id": {"S": user_id}})
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(f"SERVER_ERROR: Failed to parse UserID from Stripe callback | {error}")
        # NOTE: This is not a fatal error - we should still record transaction
        # return {
        #     "code": 500,
        #     "message": "SERVER_ERROR: Failed to parse Transaction data from Stripe callback",
        #     "error": error,
        # }

    try:
        if is_guest_purchase:
            email = obtain_email_from_cache(key=transaction_id)
        else:
            email = cw_user_record["email"]["S"]
    except:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(
            f"SERVER_ERROR: Failed to obtain email from User Record or s3 cache | {error}"
        )
        return {
            "code": 500,
            "message": "SERVER_ERROR: Failed to obtain email from User Record or s3 cache",
            "error": error,
        }

    try:
        transaction_record = create_transaction_record(
            transaction_id=transaction_id,
            shipping=shipping,
            status=status,
            amount=amount,
            email=email,
            name=name,
            commodity_list=commodity_list,
            user_id=user_id,  # 'guest', for guest purchases
            dynamo_client=dynamo_client,
        )
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(f"SERVER_ERROR: Failed to create Transaction record | {error}")
        return {
            "code": 500,
            "message": "SERVER_ERROR: Failed to create Transaction record",
            "error": error,
        }

    # NOTE:
    #   This update method would not scale (dynamo atomicity) to scores of concurrent payments.
    #   What a beautiful problem that would be to have one day!
    # NOTE:
    #   No external error handling here - as this is not a blocking error, it catches and logs any
    #   errors itself.
    # remove_purchased_commodities_from_stock(commodity_list, dynamo_client)

    # Grant DDP to user purchases
    if not is_guest_purchase:
        # NOTE:
        #   No external error handling here - as this is not a blocking error, it catches and logs any
        #   errors itself.
        grantDdpToUser(
            cw_user_record=cw_user_record,
            commodity_list=commodity_list,
            dynamo_client=dynamo_client,
        )

    # Send an email to William and Russell about completed purchase
    try:
        ses_response = send_email_order_details_to_admins(
            shipping=shipping,
            customer_name=name,
            products=commodity_list,
            amt_in_cents=amount,
            username=(None if is_guest_purchase else cw_user_record["username"]["S"]),
            is_guest_purchase=is_guest_purchase,
        )
        return {"code": 200, "message": ses_response}
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(f"SERVER_ERROR: failed to email about commodity purchase | {error}")
        return {
            "code": 500,
            "message": "SERVER_ERROR: failed to email about commodity purchase",
            "error": error,
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
    email_cache = S3_CLIENT.Bucket(TRANSACTION_EMAIL_CACHE_NAME)
    email_cache.put_object(Key=key, Body=email.encode("utf-8"))


def grantDdpToUser(cw_user_record, commodity_list, dynamo_client):
    # Count items in transaction
    item_count = 0
    for commodity in commodity_list:
        # NOTE:
        #   See cw_cart_from_short_string() for explanation of formatting
        commodity_count = int(commodity.split("_")[0])
        item_count += commodity_count

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

            # NOTE: Queue DynamoDB-Error Retries
            #   This is a very important action. Ecommerce sites, surprisingly, like to know if
            #   they have what it is they are agreeing to sell (this one does, at least).
            #   Consequently, if updating the commodity stock fails, we need to go out of our way
            #   to correct this immediately. Here, we are queueing this up for a retry lambda to
            #   take care of. Suppose dynamo errors persist still, we will at least see a
            #   high-priority lambda begin to alarm immediately.
            queue_cw_db_retry_lambda(
                controller="commerce",
                action="remove_commodity",
                db_actions=[
                    {
                        "operation": "get",
                        "table_name": "commodities",
                        "key_expression": {"product_name": {"S": product_name}},
                    },
                    {
                        "operation": "update",
                        "table_name": "commodities",
                        "key_expression": {"product_name": {"S": product_name}},
                        "field_value_map": {"quantity": new_quantity},
                    },
                ],
            )


def send_email_order_details_to_customer(
    shipping, customer_name, products, amt_in_cents, username, is_guest_purchase
):
    """"""


def send_email_order_details_to_admins(
    shipping, customer_name, products, amt_in_cents, username, is_guest_purchase
):
    ses_client = boto3.client("ses")

    if is_guest_purchase:
        cw_user_string = f"{customer_name} is a guest user."
    else:
        cw_user_string = (
            f"{customer_name} is a user of carworld.love with the username: {username}."
        )

    product_table = cw_email_product_table(products)
    customer_shipping = cw_email_format_shipping(shipping)
    dollar_cost = "%0.2f" % (amt_in_cents / 100)
    body_html = f"""
    <html>
        <head></head>
        <body>
        <h1>Car World Store: Order Detail</h1>
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

    ses_response = ses_client.send_email(
        Destination={
            "ToAddresses": EMAIL_RECIPIENTS,
        },
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
                <th>Product</th>
                <th>Quantity</th>
                <th>Size</th>
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
        size = product_details[2] if len(product_details) == 3 else ""

        cw_email_product_table_entries += f"""
          <tr>
            <td>{product_name}</td>
            <td>{quantity}</td>
            <td>{size}</td>
          </tr>
        """

    return cw_email_product_table_entries


def cw_email_format_shipping(shipping):
    shipping_html = f"""
      <p>
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
def handler(event, context):
    # parse request
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

    # initialize dynamo client
    cw_dynamo_client = CWDynamoClient()

    # direct to proper controller action
    try:
        if request["action"] == "secret":
            # Given that this is a protected action, the JWT provided in the header
            # has already been parsed, with the UserID being provided in the reqContext
            user_id = event["requestContext"]["authorizer"]["lambda"]["user_id"]

            # /secret has a request body
            request["body"] = json.loads(event["body"])

            # Create PaymentIntent
            res = create_payment_intent(
                create_payment_intent_body=request["body"],
                user_id=user_id,
                dynamo_client=cw_dynamo_client,
            )
        elif request["action"] == "cache_email":
            # /cache_email has a request body
            request["body"] = json.loads(event["body"])

            res = cache_email_action(cache_email_body=request["body"])
        elif request["action"] == "webhook":
            # /webhook has a request body
            request["body"] = json.loads(event["body"])

            res = handle_webhook(
                stripe_event=request["body"], dynamo_client=cw_dynamo_client
            )
        elif request["action"] == "commodities":
            res = get_commodity_list(dynamo_client=cw_dynamo_client)
        else:
            raise Exception(f'Invalid route: {request["action"]}')
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        print(f"SERVER_ERROR: Unhandled server error encountered -- {error}")
        return {
            "code": 500,
            "message": "SERVER_ERROR: Unhandled server error encountered",
            "error": error,
        }

    # add headers for CORS
    res["headers"] = {
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    }

    return res
