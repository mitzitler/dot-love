import os
import boto3
from twilio.rest import Client
import traceback
import uuid
from enum import Enum
from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths

# Environment Variables
USER_TABLE_NAME = os.environ["user_table_name"]
SES_SENDER_EMAIL = os.environ["ses_sender_email"]
SES_CONFIG_ID = os.environ["ses_config_id"]
SES_ADMIN_LIST = os.environ["ses_admin_list"]
TWILIO_AUTH_TOKEN = os.environ["twilio_auth_token"]
TWILIO_ACCOUNT_SID = os.environ["twilio_account_sid"]


# NOTE: Doing this at the top level so the dynamo connection is perserved b/t lambda calls
# Initialize clients
CW_DYNAMO_CLIENT = CWDynamoClient()
TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


########################################################
# Controller Action Handler
########################################################
def handler(event, context):
    # Parse request
    try:
        request = {
            "type": event["requestContext"]["http"]["method"],
            "action": event["rawPath"].replace("/gizmo/", ""),
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

    # setup log with details of call
    trace_id = str(uuid4())
    first_last = event["X-First-Last"]
    api_action = request["action"]
    log.append_keys(action=api_action, trace_id=trace_id, first_last=first_last)

    # Direct to proper controller action
    log.info(f"handling request")
    try:
        if api_action == "login":
            res = login(
                first_last=first_last,
                dynamo_client=CW_DYNAMO_CLIENT,
            )
        elif api_action == "register":
            payload = json.loads(event["body"])

            res = register(
                first_last=first_last,
                registration_fields=payload["registration_fields"],
                dynamo_client=CW_DYNAMO_CLIENT,
            )
        elif api_action == "update":
            res = update(
                first_last=first_last,
                dynamo_client=CW_DYNAMO_CLIENT,
            )
        elif api_action == "email":
            payload = json.loads(event["body"])

            res = email(
                first_last=first_last,
                template_type=payload["template_type"],
                template_details=payload["template_details"],
            )
        elif api_action == "text":
            payload = json.loads(event["body"])

            res = text(
                first_last=first_last,
                template_type=payload["template_type"],
                template_details=payload["template_details"],
            )
        else:
            raise Exception(f'Invalid route: {request["action"]}')
    except Exception as e:
        error = {
            "message": str(e),
            "stack": traceback.format_exc(),
        }
        log.error(f"SERVER_ERROR: unhandled server error encountered -- {error}")
        return {
            "code": 500,
            "message": "SERVER_ERROR: unhandled server error encountered",
            "error": error,
        }

    # TODO: See if this can be removed
    # add headers for CORS
    res["headers"] = {
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    }

    return res


########################################################
# Controller Helper Methods
########################################################
def login(first_last, dynamo_client):
    # fetch user from db
    try:
        user = User.from_first_last_db(first_last)
    except Exception as e:
        err_msg = "failed to fetch user from db"
        log.exception(err_msg)
        return {
            "code": 500,
            "message": err_msg,
            "error": e,
        }

    # user not in db
    if not user:
        err_msg = "no such user exists in db"
        log.warn(err_msg)
        return {
            "code": 404,
            "message": err_msg,
        }
    return {
        "code": 200,
        "message": "login success",
    }


def register(first_last, registration_fields, dynamo_client):
    # format user
    user = User.from_first_last_registration_fields(first_last, registration_fields)

    # register the user
    err = None
    try:
        err = user.register_db()
    except Exception as e:
        # damn
        err_msg = "failed to register user in db"
        log.exception(err_msg)
        return {
            "code": 500,
            "message": err_msg,
            "error": e,
        }

    # womp womp
    if err:
        return {"code": 400, "message": err["msg"]}

    # send text and email to let the user know their registration succeeded
    try:
        email_registration_success(user)
        text_registration_success(user)
    except Exception as e:
        # damn also
        err_msg = "failed to send user registration success text and/or email "
        log.exception(err_msg)

    return {"code": 200, "message": f"{first_last} registration success"}


# TODO
def update(first_last, dynamo_client):
    pass


# TODO
def email(first_last, template_type, template_details):
    pass


# TODO
def text(first_last, template_type, template_details):
    pass


def email_registration_success(user):
    body_html = f"""
    <html>
        <head></head>
        <body>
        <h1>RSVP Confirmation</h1>
        <hr/>
        <p>
            Thank you so much for RSVP'ing to our wedding, { user.first }!
            We are so excited for you to be there with us on our special day.
        </p>
        <p>
            We will be sure to reach out over text and email whenever we have updates to share.
            Please note, responses to this email are not being recorded and we will not see them!
            <br />
            If you wish to contact us, please reach out directly via one of the following methods:
            <br />
            <b>EMAIL:</b> themattsaucedo@gmail.com | mitzitler@gmail.com
            <b>PHONE:</b> (matthew) 352-789-4244 | (mitzi) 504-638-7943
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
            "Data": "The Wedding of Mitzi & Matthew: RSVP Confirmation",
        },
    }

    ses_response = SES_CLIENT.send_email(
        Destination={"ToAddresses": [user.address]},
        Message=email_message,
        Source=SES_SENDER_EMAIL,
        ConfigurationSetName=SES_CONFIG_ID,
    )

    return f"ses response id: {ses_response['MessageId']} | ses success code: {ses_response['ResponseMetadata']['HTTPStatusCode']}."


def text_registration_success(user):
    text_body = f"""
    Thank you so much for RSVP'ing to our wedding, { user.first }!
    We are so excited for you to be there with us on our special day.

    We will be sure to reach out over text and email whenever we have updates to share.

    Please note, responses to this phone number are not being recorded and we will not see them!
    If you wish to contact us, please reach out directly via one of the following methods:
    EMAIL: themattsaucedo@gmail.com | mitzitler@gmail.com
    PHONE: (matthew) 352-789-4244 | (mitzi) 504-638-7943
    """

    TWILIO_CLIENT.messages.create(
        body=f"", from_=TWILIO_SENDER_NUMBER, to=user.address.phone
    )


########################################################
# Class Defs
########################################################
class UserAddress:
    def __init__(self, street, second, city, zipcode, country, state, phone):
        self.street = street
        self.second = second
        self.city = city
        self.zipcode = zipcode
        self.country = country
        self.state = state
        self.phone = phone


class UserDiet:
    def __init__(
        self, alcohol, meat, dairy, fish, shellfish, eggs, gluten, peanuts, restrictions
    ):
        self.alcohol = alcohol
        self.meat = meat
        self.dairy = dairy
        self.fish = fish
        self.shellfish = shellfish
        self.eggs = eggs
        self.gluten = gluten
        self.peanuts = peanuts
        self.restrictions = restrictions


class GuestDetails:
    def __init__(self, link, pair_first_last):
        self.link = link
        self.pair_first_last = pair_first_last


class RsvpStatus(Enum):
    UNDECIDED = 1
    ATTENDING = 2
    NOTATTENDING = 3


class Pronouns(Enum):
    SHEHER = 1
    HEHIM = 2
    THEYTHEM = 3
    SHETHEY = 4
    HETHEY = 5


class User:
    def __init__(
        self,
        first,
        last,
        rsvp_code,
        rsvp_status,
        pronouns,
        user_address,
        user_diet,
        guest_details=None,
    ):
        self.first = first
        self.last = last
        self.rsvp_code = rsvp_code
        self.rsvp_status = rsvp_status
        self.pronouns = pronouns
        self.address = user_address
        self.user_diet = user_diet
        self.guest_details = guest_details

    @staticmethod
    def from_first_last_db(first_last):
        first = first_last.split("_")[0]
        last = first_last.split("_")[1]
        pass

    @staticmethod
    def from_first_last_registration_fields(first_last, registration_fields):
        first = first_last.split("_")[0]
        last = first_last.split("_")[1]

        rsvp_status = RsvpStatus(registration_fields["rsvp_status"])
        pronouns = Pronouns(registration_fields["pronouns"])
        address = UserAddress(
            registration_fields["street"],
            registration_fields["second"],
            registration_fields["city"],
            registration_fields["zipcode"],
            registration_fields["country"],
            registration_fields["state"],
            registration_fields["phone"],
        )
        diet = UserDiet(
            registration_fields["alcohol"],
            registration_fields["meat"],
            registration_fields["dairy"],
            registration_fields["fish"],
            registration_fields["shellfish"],
            registration_fields["eggs"],
            registration_fields["gluten"],
            registration_fields["peanuts"],
            registration_fields["restrictions"],
        )
        guest_details = GuestDetails(
            registration_fields["link"], registration_fields["pair_first_last"]
        )

        return User(
            first=first,
            last=last,
            rsvp_code=registration_fields["rsvp_code"],
            rsvp_status=rsvp_status,
            pronouns=pronouns,
            user_address=address,
            user_diet=diet,
            guest_details=guest_details,
        )


########################################################
# CWDynamo Client
########################################################
# TODO: Make this into a lambda layer to be used as a common Lib
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
