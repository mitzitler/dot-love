import json
import os
import random
import string
import traceback
from functools import wraps
from boto3.dynamodb.types import TypeDeserializer
import uuid
from enum import Enum

from aws_lambda_powertools.event_handler import Response

# TODO: from aws_lambda_powertools.event_handler import Response
# ex:
# return Response(
#     status_code=200,
#     content_type="application/json",
#     body={"code": 200, "message": "success"},
# )

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.api_gateway import (
    APIGatewayHttpResolver,
    ProxyEventType,
)
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from twilio.rest import Client

# Environment Variables
USER_TABLE_NAME = os.environ["user_table_name"]
SURVEY_RESULTS_TABLE_NAME = os.environ["survey_results_table_name"]
INTERNAL_API_KEY = os.environ["internal_api_key"]
SES_SENDER_EMAIL = os.environ["ses_sender_email"]
SES_CONFIG_ID = os.environ["ses_config_id"]
SES_ADMIN_LIST = os.environ["ses_admin_list"]
TWILIO_AUTH_TOKEN = os.environ["twilio_auth_token"]
TWILIO_ACCOUNT_SID = os.environ["twilio_account_sid"]
TWILIO_SENDER_NUMBER = os.environ["twilio_sender_number"]
INTERNAL_ROUTE_LIST = ["ping", "list", "text", "email"]
CONTACT_INFO = {
    "mitzi": {
        "phone": os.environ["mitzi_phone"],
        "email": os.environ["mitzi_email"],
    },
    "matthew": {
        "phone": os.environ["matthew_phone"],
        "email": os.environ["matthew_email"],
    },
    "ginny": {
        "phone": os.environ["ginny_phone"],
    },
}
RSVP_CODE_OPEN_PLUS_ONE = os.environ["open_plus_one_code"]

# Twilio texts
RSVP_NO_TEXT = """
⛔ RSVP Confirmed ⛔

Thank you so much for filling out your RSVP form for our wedding!
We are sorry you won't be able to attend, but we hope to see you soon anyway!

We will be updating our website, www.mitzimatthew.love, soon with our registry! 🎁
We'll send an update to all those invited once that's done 😁
"""

RSVP_CONFIRMED_TEXT = """
🎉 RSVP Confirmed! 🎉

Thank you so much for RSVP'ing to our wedding, {first_name}!
We are so excited for you to be there with us on our special day 💒💕

Please save this number into your contacts 📲, as we will continue to use it to communicate important information regarding our wedding! 📢

We will be sure to reach out over text 📱 and email 📨 whenever we have updates to share - especially regarding our website, www.mitzimatthew.love!

Please note, responses to this phone number are not being recorded and we will not see them! 🙈

If you wish to contact us, please reach out directly via one of the following methods:

Matthew:
📨 themattsaucedo@gmail.com
📱 +1 (352) 789-4244

Mitzi:
📨 mitzitler@gmail.com
📱 +1 (504) 638-7943
"""

ADMIN_RSVP_ALERT_TEXT = """
{first} {last} has RSVP'd to the wedding! ⭐🎉
"""

PLUS_ONE_TEXT = """
🌟 Plus-One Alert! 🌟

Hey {first_name}, we have some exciting news! 🎉 You get to bring a +1 to our wedding! 💃🕺💕

To make it official, your guest just needs to RSVP at this custom link we made just for you!:
👉 www.mitzimatthew.love/rsvp/guest?code={guest_code}

Can’t wait to celebrate with you! 🥂🎶💒
"""

ADMIN_RSVP_ALERT_PLUS_ONE_TEXT = """
{first} {last} has RSVP'd to the wedding! ⭐🎉
They also have a PLUS ONE! 😁
"""

INVITER_GUEST_RSVPD_TEXT = """
👭 Your Guest has RSVP'd! 👬

Hey {inviter_first}, great news! Your guest, {invitee_first}, has successfully RSVP'd to Mitzi and Matthew's wedding!
🕺🏻💃
"""

# Powertools logger
log = Logger(service="gizmo")

# Powertools routing
app = APIGatewayHttpResolver()


########################################################
# Controller Helper Methods
########################################################
def email_registration_success(user):
    if user.rsvp_status is RsvpStatus.NOTATTENDING:
        return

    if user.guest_details.date_link_requested:
        DOT_LOVE_MESSAGE_CLIENT.email(
            DotLoveMessageType.REGISTRATION_SUCCESS_EMAIL_WITH_GUEST,
            {
                "first": user.first,
                "user_info_table": user.as_html_table(has_guest=True),
            },
            user.email,
        )
        return
    DOT_LOVE_MESSAGE_CLIENT.email(
        DotLoveMessageType.REGISTRATION_SUCCESS_EMAIL_NO_GUEST,
        {
            "first": user.first,
            "user_info_table": user.as_html_table(has_guest=False),
        },
        user.email,
    )
    return


def text_admins(message):
    TWILIO_CLIENT.messages.create(
        body=message.strip(),
        from_=TWILIO_SENDER_NUMBER,
        to=CONTACT_INFO["mitzi"]["phone"],
    )
    TWILIO_CLIENT.messages.create(
        body=message.strip(),
        from_=TWILIO_SENDER_NUMBER,
        to=CONTACT_INFO["matthew"]["phone"],
    )
    # bc she asked
    TWILIO_CLIENT.messages.create(
        body=message.strip(),
        from_=TWILIO_SENDER_NUMBER,
        to=CONTACT_INFO["ginny"]["phone"],
    )


def text_registration_success(user, inviter):
    if user.rsvp_status is RsvpStatus.NOTATTENDING:
        TWILIO_CLIENT.messages.create(
            body=plus_one_text_body.strip(),
            from_=TWILIO_SENDER_NUMBER,
            to=user.address.phone,
        )
        text_admins(f"{user.first} {user.last} isn't coming 🖕🙄🖕")
        return

    # text admins
    admin_text_body = ADMIN_RSVP_ALERT_TEXT.format(first=user.first, last=user.last)
    if user.guest_details.date_link_requested:
        admin_text_body = ADMIN_RSVP_ALERT_PLUS_ONE_TEXT.format(
            first=user.first, last=user.last
        )
    text_admins(admin_text_body)

    # text user
    rsvp_text_body = RSVP_CONFIRMED_TEXT.format(
        first_name=user.first,
        matthew_email=CONTACT_INFO["matthew"]["email"],
        matthew_phone=CONTACT_INFO["matthew"]["phone"],
        mitzi_email=CONTACT_INFO["mitzi"]["email"],
        mitzi_phone=CONTACT_INFO["mitzi"]["phone"],
    )
    TWILIO_CLIENT.messages.create(
        body=rsvp_text_body.strip(), from_=TWILIO_SENDER_NUMBER, to=user.address.phone
    )

    plus_one_text_body = PLUS_ONE_TEXT.format(
        first_name=user.first, guest_code=user.guest_details.link
    )
    if user.guest_details.date_link_requested:
        TWILIO_CLIENT.messages.create(
            body=plus_one_text_body.strip(),
            from_=TWILIO_SENDER_NUMBER,
            to=user.address.phone,
        )
    if inviter:
        inviter_text_body = INVITER_GUEST_RSVPD_TEXT.format(
            inviter_first=inviter.first, invitee_first=user.first
        )
        TWILIO_CLIENT.messages.create(
            body=plus_one_text_body.strip(),
            from_=TWILIO_SENDER_NUMBER,
            to=inviter.address.phone,
        )


########################################################
# Class Defs
########################################################
class DotLoveMessageType(Enum):
    REGISTRATION_SUCCESS_EMAIL_WITH_GUEST = 1
    REGISTRATION_SUCCESS_EMAIL_NO_GUEST = 2
    RSVP_REMINDER_EMAIL = 3
    REGISTRATION_SUCCESS_TEXT = 4
    REGISTRATION_SUCCESS_NOT_COMING_TEXT = 5
    RAW_TEXT = 6
    ITEM_CLAIMED_TEXT = 7
    ITEM_CLAIMED_TEXT_ADMINS = 8
    SURVEY_ALERT = 9

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"DotLoveMessageType.{self.name}"


class DotLoveMessageClient:
    def __init__(self, ses_client, sender_email, config_id):
        """
        Initialize the DotLoveMessageClient with an SES client, sender email, and configuration set ID.

        :param ses_client: The AWS SES client.
        :param sender_email: The email address to use as the sender.
        :param config_id: The configuration set ID for SES.
        """
        self.ses_client = ses_client
        self.sender_email = sender_email
        self.config_id = config_id

        # For attaching to emails
        self.contact_table = f"""
        <table border="1" style="border-collapse: collapse; text-align: left;">
            <tr>
                <th></th>
                <th>Email</th>
                <th>Phone</th>
            </tr>
            <tr>
                <td>Matthew</td>
                <td>{CONTACT_INFO['matthew']['email']}</td>
                <td>{CONTACT_INFO['matthew']['phone']}</td>
            </tr>
            <tr>
                <td>Mitzi</td>
                <td>{CONTACT_INFO['mitzi']['email']}</td>
                <td>{CONTACT_INFO['mitzi']['phone']}</td>
            </tr>
        </table>
        """

    def email(self, message_type, template_input, recipient_email):
        """
        Send an email based on the message type and template input.

        :param message_type: The type of message to send.
        :param template_input: A dictionary with template variables for interpolation.
        :return: The SES response ID and status code.
        """
        template = self._get_email_template(message_type)

        template_input["contact_table"] = self.contact_table
        body_html = template["body"].format(**template_input)

        email_message = {
            "Body": {
                "Html": {
                    "Charset": "utf-8",
                    "Data": body_html,
                },
            },
            "Subject": {
                "Charset": "utf-8",
                "Data": template["title"],
            },
        }

        ses_response = self.ses_client.send_email(
            Destination={"ToAddresses": [recipient_email]},
            Message=email_message,
            Source=self.sender_email,
            ConfigurationSetName=self.config_id,
        )

        return f"SES response ID: {ses_response['MessageId']} | SES success code: {ses_response['ResponseMetadata']['HTTPStatusCode']}."

    def _get_text_template(self, message_type):
        """
        Retrieve the text template corresponding to the message type.

        :param message_type: The type of message.
        :return: The text template as a string.
        """
        message_type_enum = DotLoveMessageType[message_type]
        templates = {
            DotLoveMessageType.REGISTRATION_SUCCESS_TEXT: """
🎉 RSVP Confirmed! 🎉

Thank you so much for RSVP'ing to our wedding, {first_name}!
We are so excited for you to be there with us on our special day 💒💕

Please save this number into your contacts 📲, as we will continue to use it to communicate important information regarding our wedding! 📢

We will be sure to reach out over text 📱 and email 📨 whenever we have updates to share - especially regarding our website, www.mitzimatthew.love!

Please note, responses to this phone number are not being recorded and we will not see them! 🙈

If you wish to contact us, please reach out directly via one of the following methods:

Matthew:
📨 {matthew_email}
📱 {matthew_phone}

Mitzi:
📨 {mitzi_email}
📱 {mitzi_phone}

""",
            DotLoveMessageType.REGISTRATION_SUCCESS_NOT_COMING_TEXT: """
⛔ RSVP Confirmed ⛔

Thank you so much for filling out your RSVP form for our wedding!
We are sorry you won't be able to attend, but we hope to see you soon anyway!

We will be updating our website, www.mitzimatthew.love, soon with our registry! 🎁
We'll send an update to all those invited once that's done 😁
""",
            DotLoveMessageType.RAW_TEXT: """
{raw}
""",
            DotLoveMessageType.ITEM_CLAIMED_TEXT: """
🎁 Registry Item Claimed! 🎁

Thank you so much for claiming {item_name}, {first_name}! 💖
This helps us keep track of gifts and avoid duplicates. We really appreciate your generosity! 💕

If you would like, you can send this item directly to our address:
{mitzi_matthew_address}

If you change your mind or are no longer able to gift this item, no worries at all —
just head over to www.mitzimatthew.love/registry and unclaim it when you can 🧑‍💻💫

Much love,
Mitzi & Matthew 💕
""",
            DotLoveMessageType.ITEM_CLAIMED_TEXT_ADMINS: """
🎁 Registry Item Claimed! 🎁

The item, {item_name}, was claimed by {first_name}! 🎉

Woohoo! 💕
""",
            DotLoveMessageType.SURVEY_ALERT: """
📋 Quick Survey! 📋

Hi {first_name}! We have a short survey for you to help us plan the perfect wedding day 💒

Please take a moment to fill it out at:
www.mitzimatthew.love/survey

Thank you so much! 💕
Mitzi & Matthew
""",
        }
        return templates[message_type_enum]

    def _get_email_template(self, message_type):
        """
        Retrieve the email template corresponding to the message type.

        :param message_type: The type of message.
        :return: The email template as a string.
        """
        templates = {
            DotLoveMessageType.REGISTRATION_SUCCESS_EMAIL_WITH_GUEST: {
                "title": "The Wedding of Mitzi & Matthew: RSVP Confirmation",
                "body": """
            <html>
                <head></head>
                <body>
                <h1>RSVP Confirmation</h1>
                <hr/>
                <p>
                    Thank you so much for RSVP'ing to our wedding, {first}!
                    We are so excited for you to be there with us on our special day.
                </p>
                <p>
                    The information you shared is as follows:

                    {user_info_table}
                </p>
                <p>
                    Please note the guest link included above! As you have been allotted an extra guest invite,
                    we've taken the liberty of creating a signup URL for them. Your guest will need to use this
                    link to RSVP for the wedding.

                    If any of this information looks incorrect, please login with your first
                    and last name at <a href="www.mitzimatthew.love">www.mitzimatthew.love</a> to update your info!
                <p>
                <p>
                    We will be sure to reach out over text and email whenever we have updates to share.
                    Please note, responses to this email are not being recorded and we will not see them!
                    <br />
                    If you wish to contact us, please reach out directly via one of the following methods:
                    <br />
                    {contact_table}
                </p>
                </body>
            </html>
            """,
            },
            DotLoveMessageType.REGISTRATION_SUCCESS_EMAIL_NO_GUEST: {
                "title": "The Wedding of Mitzi & Matthew: RSVP Confirmation",
                "body": """
            <html>
                <head></head>
                <body>
                <h1>RSVP Confirmation</h1>
                <hr/>
                <p>
                    Thank you so much for RSVP'ing to our wedding, {first}!
                    We are so excited for you to be there with us on our special day.
                </p>
                <p>
                    The information you shared is as follows:

                    {user_info_table}
                </p>
                <p>
                    If any of this information looks incorrect, please login with your first
                    and last name at <a href="www.mitzimatthew.love">www.mitzimatthew.love</a> to update your info!
                <p>
                <p>
                    We will be sure to reach out over text and email whenever we have updates to share.
                    Please note, responses to this email are not being recorded and we will not see them!
                    <br />
                    If you wish to contact us, please reach out directly via one of the following methods:
                    <br />
                    {contact_table}
                </p>
                </body>
            </html>
            """,
            },
        }
        return templates[message_type]

    def text(self, message_type, template_input, recipient_phone):
        """
        Send a text based on the message type and template input.

        :param message_type: The type of message to send.
        :param template_input: A dictionary with template variables for interpolation.
        # TODO: Validate this is oneof registered user
        :param recipient_phone: Phone number to text.
        :return: None
        """
        template = self._get_text_template(message_type)
        text_body = template.format(**template_input).strip()

        TWILIO_CLIENT.messages.create(
            body=text_body,
            from_=TWILIO_SENDER_NUMBER,
            to=recipient_phone,
        )

        if message_type == DotLoveMessageType.ITEM_CLAIMED_TEXT.name:
            # not used in this template
            del template_input["mitzi_matthew_address"]

            admin_template = self._get_text_template(
                DotLoveMessageType.ITEM_CLAIMED_TEXT_ADMINS.name
            )
            text_body = admin_template.format(**template_input).strip()
            text_admins(text_body)

    def text_blast(self, message_type, template_input, numbers):
        """
        Send a text blast based on the message type and template input.

        :param message_type: The type of message to send.
        :param template_input: A dictionary with template variables for interpolation.
        :param recipient_phone: Number list.
        :return: None
        """
        template = self._get_text_template(message_type)
        text_body = template.format(**template_input).strip()

        for number in numbers:
            try:
                TWILIO_CLIENT.messages.create(
                    body=text_body, from_=TWILIO_SENDER_NUMBER, to=number
                )
            except Exception as e:
                log.exception("failed to send text to number=" + number)
                continue


class UserAddress:
    def __init__(self, street, second_line, city, zipcode, country, state_loc, phone):
        self.street = street
        self.second_line = second_line
        self.city = city
        self.zipcode = zipcode
        self.country = country
        self.state_loc = state_loc
        self.phone = phone

    def as_map(self):
        return {
            "street": self.street,
            "second_line": self.second_line,
            "city": self.city,
            "zipcode": self.zipcode,
            "country": self.country,
            "state_loc": self.state_loc,
            "phone": self.phone,
        }

    def as_map(self):
        return {
            "street": self.street,
            "second_line": self.second_line,
            "city": self.city,
            "zipcode": self.zipcode,
            "country": self.country,
            "state_loc": self.state_loc,
            "phone": self.phone,
        }

    def __str__(self):
        return (
            f"UserAddress(street={self.street}, second_line={self.second_line}, "
            f"city={self.city}, zipcode={self.zipcode}, country={self.country}, "
            f"state_loc={self.state_loc}, phone={self.phone})"
        )

    def __repr__(self):
        return (
            f"UserAddress(street={self.street!r}, second_line={self.second_line!r}, "
            f"city={self.city!r}, zipcode={self.zipcode!r}, country={self.country!r}, "
            f"state_loc={self.state_loc!r}, phone={self.phone!r})"
        )


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

    def as_map(self):
        return {
            "alcohol": self.alcohol,
            "meat": self.meat,
            "dairy": self.dairy,
            "fish": self.fish,
            "shellfish": self.shellfish,
            "eggs": self.eggs,
            "gluten": self.gluten,
            "peanuts": self.peanuts,
            "restrictions": self.restrictions,
        }

    def __str__(self):
        return (
            f"UserDiet(alcohol={self.alcohol}, meat={self.meat}, dairy={self.dairy}, "
            f"fish={self.fish}, shellfish={self.shellfish}, eggs={self.eggs}, "
            f"gluten={self.gluten}, peanuts={self.peanuts}, restrictions={self.restrictions})"
        )

    def __repr__(self):
        return (
            f"UserDiet(alcohol={self.alcohol!r}, meat={self.meat!r}, dairy={self.dairy!r}, "
            f"fish={self.fish!r}, shellfish={self.shellfish!r}, eggs={self.eggs!r}, "
            f"gluten={self.gluten!r}, peanuts={self.peanuts!r}, restrictions={self.restrictions!r})"
        )


class GuestDetails:
    def __init__(self, link, pair_first_last, date_link_requested):
        self.link = link
        self.pair_first_last = pair_first_last
        self.date_link_requested = date_link_requested

    def as_map(self):
        return {
            "link": self.link,
            "pair_first_last": self.pair_first_last,
            "date_link_requested": self.date_link_requested,
        }

    def __str__(self):
        return f"GuestDetails(link={self.link}, pair_first_last={self.pair_first_last})"

    def __repr__(self):
        return f"GuestDetails(link={self.link!r}, pair_first_last={self.pair_first_last!r})"


class RsvpStatus(Enum):
    UNDECIDED = 1
    ATTENDING = 2
    NOTATTENDING = 3

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"RsvpStatus.{self.name}"


class Pronouns(Enum):
    SHE_HER = 1
    HE_HIM = 2
    THEY_THEM = 3
    SHE_THEY = 4
    HE_THEY = 5

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Pronouns.{self.name}"


class User:
    def __init__(
        self,
        first,
        last,
        rsvp_code,
        rsvp_status,
        pronouns,
        address,
        email,
        diet,
        guest_details=None,
        guest_type=None,
        rehearsal_dinner_invited=False,
    ):
        self.first = first
        self.last = last
        self.rsvp_code = rsvp_code
        self.rsvp_status = rsvp_status
        self.pronouns = pronouns
        self.email = email
        self.address = address
        self.diet = diet
        self.guest_details = guest_details
        self.guest_type = guest_type
        self.rehearsal_dinner_invited = rehearsal_dinner_invited

    def as_map(self):
        return {
            "first": self.first,
            "last": self.last,
            "rsvp_code": self.rsvp_code,
            "rsvp_status": self.rsvp_status.name if self.rsvp_status else None,
            "pronouns": self.pronouns.name if self.pronouns else None,
            "email": self.email,
            "address": self.address.as_map() if self.address else None,
            "diet": self.diet.as_map() if self.diet else None,
            "guest_details": (
                self.guest_details.as_map() if self.guest_details else None
            ),
            "guest_type": self.guest_type,
            "rehearsal_dinner_invited": self.rehearsal_dinner_invited,
        }

    def __str__(self):
        return (
            f"User(first={self.first}, last={self.last}, rsvp_code={self.rsvp_code}, "
            f"rsvp_status={self.rsvp_status}, pronouns={self.pronouns}, email={self.email}, "
            f"address={self.address}, diet={self.diet}, guest_details={self.guest_details}, "
            f"guest_type={self.guest_type}, rehearsal_dinner_invited={self.rehearsal_dinner_invited})"
        )

    def __repr__(self):
        return (
            f"User(first={self.first!r}, last={self.last!r}, rsvp_code={self.rsvp_code!r}, "
            f"rsvp_status={self.rsvp_status!r}, pronouns={self.pronouns!r}, email={self.email!r}, "
            f"address={self.address!r}, diet={self.diet!r}, guest_details={self.guest_details!r}, "
            f"guest_type={self.guest_type!r}, rehearsal_dinner_invited={self.rehearsal_dinner_invited!r})"
        )

    def as_html_table(self, has_guest):
        # Start the table with a title row
        table_html = (
            f"<table>\n<tr><th colspan='2'>{self.first} {self.last}</th></tr>\n"
        )

        # Define a mapping for user-friendly labels
        friendly_labels = {
            "first": "First Name",
            "last": "Last Name",
            "email": "Email",
            "address": "Address",
            "diet": "Dietary Preferences",
            "rsvp_status": "RSVP Status",
            "pronouns": "Pronouns",
        }
        pronoun_map = {
            Pronouns.SHE_HER: "she/her",
            Pronouns.HE_HIM: "he/him",
            Pronouns.THEY_THEM: "they/them",
            Pronouns.SHE_THEY: "she/they",
            Pronouns.HE_THEY: "he/they",
        }

        # Add each attribute as a row
        for key, value in self.as_map().items():
            if key in {"rsvp_code"}:
                continue

            # Use friendly labels or fall back to capitalized field name
            label = friendly_labels.get(key, key.replace("_", " ").capitalize())

            # Special handling for pronouns
            if key == "pronouns" and value in pronoun_map:
                value = pronoun_map[value]

            # Convert nested dictionaries or complex types to a string representation
            # TODO: Make this more readable
            if isinstance(value, dict):
                formatted_lines = []
                for k, v in value.items():
                    if v is not None and (k != "link" or has_guest):
                        # modify value
                        if k == "link":
                            formatted_value = f'<a href="www.mitzimatthew.love/rsvp/guest?code={self.guest_details.link}">www.mitzimatthew.love/rsvp/guest?code={self.guest_details.link}</a>'
                        else:
                            formatted_value = v

                        # modify key
                        formatted_key = k
                        if formatted_key == "pair_first_last":
                            formatted_key = "date"
                        formatted_key.replace("_", " ").capitalize()

                        # Format the line
                        formatted_line = f"{formatted_key}: {formatted_value}"
                        formatted_lines.append(formatted_line)
                value = "<br>".join(formatted_lines)
            elif isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            elif value is None:
                value = "N/A"

            # Add a table row for the attribute
            table_html += f"<tr><td>{label}</td><td>{value}</td></tr>\n"

        # Close the table
        table_html += "</table>"
        return table_html

    @staticmethod
    def from_first_last_db(first_last, dynamo_client):
        key_expression = {"first_last": {"S": first_last.lower()}}
        db_user = dynamo_client.get(USER_TABLE_NAME, key_expression)
        if not db_user:
            return None

        return User(
            first=first_last.split("_")[0].lower(),
            last=first_last.split("_")[1].lower(),
            rsvp_code=db_user["rsvp_code"]["S"],
            rsvp_status=RsvpStatus[db_user["rsvp_status"]["S"]],
            pronouns=Pronouns[db_user["pronouns"]["S"]],
            address=UserAddress(
                street=db_user["street"]["S"],
                second_line=db_user["second_line"]["S"],
                city=db_user["city"]["S"],
                zipcode=db_user["zipcode"]["S"],
                country=db_user["country"]["S"],
                state_loc=db_user["state_loc"]["S"],
                phone=db_user["phone"]["S"],
            ),
            email=db_user["email"]["S"],
            diet=UserDiet(
                alcohol=bool(db_user["alcohol"]["BOOL"]),
                meat=bool(db_user["meat"]["BOOL"]),
                dairy=bool(db_user["dairy"]["BOOL"]),
                fish=bool(db_user["fish"]["BOOL"]),
                shellfish=bool(db_user["shellfish"]["BOOL"]),
                eggs=bool(db_user["eggs"]["BOOL"]),
                gluten=bool(db_user["gluten"]["BOOL"]),
                peanuts=bool(db_user["peanuts"]["BOOL"]),
                restrictions=db_user["restrictions"]["S"],
            ),
            guest_details=GuestDetails(
                link=db_user["guest_link"]["S"],
                pair_first_last=db_user["guest_pair_first_last"]["S"],
                date_link_requested=db_user["date_link_requested"]["BOOL"],
            ),
            guest_type=db_user.get("guest_type", {}).get("S"),
            rehearsal_dinner_invited=bool(db_user.get("rehearsal_dinner_invited", {}).get("BOOL", False)),
        )

    @staticmethod
    def list_db(dynamo_client):
        db_users = dynamo_client.get_all(USER_TABLE_NAME)
        if not db_users:
            return None

        user_list = []
        for db_user in db_users:
            user = User(
                first=db_user["first_last"]["S"].split("_")[0].lower(),
                last=db_user["first_last"]["S"].split("_")[1].lower(),
                rsvp_code=db_user["rsvp_code"]["S"],
                rsvp_status=RsvpStatus[db_user["rsvp_status"]["S"]],
                pronouns=Pronouns[db_user["pronouns"]["S"]],
                address=UserAddress(
                    street=db_user["street"]["S"],
                    second_line=db_user["second_line"]["S"],
                    city=db_user["city"]["S"],
                    zipcode=db_user["zipcode"]["S"],
                    country=db_user["country"]["S"],
                    state_loc=db_user["state_loc"]["S"],
                    phone=db_user["phone"]["S"],
                ),
                email=db_user["email"]["S"],
                diet=UserDiet(
                    alcohol=bool(db_user["alcohol"]["BOOL"]),
                    meat=bool(db_user["meat"]["BOOL"]),
                    dairy=bool(db_user["dairy"]["BOOL"]),
                    fish=bool(db_user["fish"]["BOOL"]),
                    shellfish=bool(db_user["shellfish"]["BOOL"]),
                    eggs=bool(db_user["eggs"]["BOOL"]),
                    gluten=bool(db_user["gluten"]["BOOL"]),
                    peanuts=bool(db_user["peanuts"]["BOOL"]),
                    restrictions=db_user["restrictions"]["S"],
                ),
                guest_details=GuestDetails(
                    link=db_user["guest_link"]["S"],
                    pair_first_last=db_user["guest_pair_first_last"]["S"],
                    date_link_requested=db_user["date_link_requested"]["BOOL"],
                ),
                guest_type=db_user.get("guest_type", {}).get("S"),
                rehearsal_dinner_invited=bool(db_user.get("rehearsal_dinner_invited", {}).get("BOOL", False)),
            )
            user_list.append(user)

        return user_list

    @staticmethod
    def from_guest_link_db(guest_link, dynamo_client):
        # TODO: Move client logic into query itself, instead of accessing the raw client
        # here directly
        db_user = dynamo_client.client.query(
            TableName=USER_TABLE_NAME,
            IndexName="guest-link-lookup-index",
            KeyConditionExpression="#gl = :value",
            ExpressionAttributeNames={"#gl": "guest_link"},
            ExpressionAttributeValues={":value": {"S": guest_link}},
        ).get("Items", [None])
        if not db_user:
            log.warning(f"guest with link code {guest_link} not found")
            return None
        db_user = db_user[0]

        return User(
            first=db_user["first_last"]["S"].split("_")[0],
            last=db_user["first_last"]["S"].split("_")[1],
            rsvp_code=db_user["rsvp_code"]["S"],
            rsvp_status=RsvpStatus[db_user["rsvp_status"]["S"]],
            pronouns=Pronouns[db_user["pronouns"]["S"]],
            address=UserAddress(
                street=db_user["street"]["S"],
                second_line=db_user["second_line"]["S"],
                city=db_user["city"]["S"],
                zipcode=db_user["zipcode"]["S"],
                country=db_user["country"]["S"],
                state_loc=db_user["state_loc"]["S"],
                phone=db_user["phone"]["S"],
            ),
            email=db_user["email"]["S"],
            diet=UserDiet(
                alcohol=bool(db_user["alcohol"]["BOOL"]),
                meat=bool(db_user["meat"]["BOOL"]),
                dairy=bool(db_user["dairy"]["BOOL"]),
                fish=bool(db_user["fish"]["BOOL"]),
                shellfish=bool(db_user["shellfish"]["BOOL"]),
                eggs=bool(db_user["eggs"]["BOOL"]),
                gluten=bool(db_user["gluten"]["BOOL"]),
                peanuts=bool(db_user["peanuts"]["BOOL"]),
                restrictions=db_user["restrictions"]["S"],
            ),
            guest_details=GuestDetails(
                link=db_user["guest_link"]["S"],
                pair_first_last=db_user["guest_pair_first_last"]["S"],
                date_link_requested=db_user["date_link_requested"]["BOOL"],
            ),
            guest_type=db_user.get("guest_type", {}).get("S"),
            rehearsal_dinner_invited=bool(db_user.get("rehearsal_dinner_invited", {}).get("BOOL", False)),
        )

    @staticmethod
    def extract_users_from_rsvps(rsvps):
        users = []
        for rsvp in rsvps:
            users.append(User.from_client_rsvp(rsvp))
        return users

    @staticmethod
    def from_client_rsvp(guest_info):
        first = guest_info["firstName"].lower().rstrip().lstrip()
        last = guest_info["lastName"].lower().rstrip().lstrip()
        guest_link_string = "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(4)
        )

        # paranoid country code checks
        country_code = (
            guest_info["phoneNumberCountryCode"]
            .replace(" ", "")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace("+", "")
        )
        if not country_code.isdigit():
            logger.info("how, literally how")
            country_code = "1"

        phone = (
            "+"
            + country_code
            + guest_info["phoneNumber"]
            .replace(" ", "")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
        )

        rsvp_status = RsvpStatus[guest_info["rsvpStatus"].upper()]
        pronouns = Pronouns[
            guest_info["pronouns"].replace("/", "_").replace(" ", "").upper()
        ]
        address = UserAddress(
            guest_info["streetAddress"],
            guest_info["secondAddress"],
            guest_info["city"],
            guest_info["zipcode"],
            guest_info["country"],
            guest_info["stateProvince"],
            phone,
        )
        email = guest_info["email"]
        diet = UserDiet(
            guest_info["drinkAlcohol"],
            guest_info["eatMeat"],
            guest_info["eatDairy"],
            guest_info["eatFish"],
            guest_info["eatShellfish"],
            guest_info["eatEggs"],
            guest_info["eatGluten"],
            guest_info["eatPeanuts"],
            guest_info["moreRestrictions"],
        )
        guest_details = GuestDetails(
            link=guest_link_string,
            pair_first_last=guest_info.get("pairFirstLast", ""),
            date_link_requested=guest_info.get("dateLinkRequested", False),
        )

        return User(
            first=first,
            last=last,
            rsvp_code=guest_info["rsvpCode"],
            rsvp_status=rsvp_status,
            pronouns=pronouns,
            address=address,
            email=email,
            diet=diet,
            guest_details=guest_details,
        )

    def register_db(self, dynamo_client):
        key_expression = {"first_last": {"S": self.first + "_" + self.last}}

        field_value_map = {
            # basic details
            "rsvp_code": self.rsvp_code,
            "rsvp_status": self.rsvp_status.name,
            "pronouns": self.pronouns.name,
            "email": self.email,
            # diet
            "alcohol": self.diet.alcohol,
            "meat": self.diet.meat,
            "dairy": self.diet.dairy,
            "fish": self.diet.fish,
            "shellfish": self.diet.shellfish,
            "eggs": self.diet.eggs,
            "gluten": self.diet.gluten,
            "peanuts": self.diet.peanuts,
            "restrictions": self.diet.restrictions,
            # guest info
            "guest_link": self.guest_details.link,
            "date_link_requested": self.guest_details.date_link_requested,
            "guest_pair_first_last": self.guest_details.pair_first_last,
            # address
            "street": self.address.street,
            "second_line": self.address.second_line,
            "city": self.address.city,
            "zipcode": self.address.zipcode,
            "country": self.address.country,
            "state_loc": self.address.state_loc,
            "phone": self.address.phone,
            # guest classification
            "rehearsal_dinner_invited": self.rehearsal_dinner_invited,
        }

        # Add guest_type only if it's not None (nullable field)
        if self.guest_type is not None:
            field_value_map["guest_type"] = self.guest_type

        dynamo_client.create(
            USER_TABLE_NAME,
            key_expression,
            field_value_map,
        )

    def update_db(self, dynamo_client):
        key_expression = {"first_last": {"S": self.first + "_" + self.last}}
        field_value_map = {
            # basic details
            "rsvp_code": self.rsvp_code,
            "rsvp_status": self.rsvp_status.name,
            "pronouns": self.pronouns.name,
            # diet
            "alcohol": self.diet.alcohol,
            "meat": self.diet.meat,
            "dairy": self.diet.dairy,
            "fish": self.diet.fish,
            "shellfish": self.diet.shellfish,
            "eggs": self.diet.eggs,
            "gluten": self.diet.gluten,
            "peanuts": self.diet.peanuts,
            "restrictions": self.diet.restrictions,
            # guest info
            "guest_link": self.guest_details.link,
            "guest_pair_first_last": self.guest_details.pair_first_last,
            # address
            "street": self.address.street,
            "second_line": self.address.second_line,
            "city": self.address.city,
            "zipcode": self.address.zipcode,
            "country": self.address.country,
            "state_loc": self.address.state_loc,
            "phone": self.address.phone,
            # guest classification
            "rehearsal_dinner_invited": self.rehearsal_dinner_invited,
        }

        # Add guest_type only if it's not None (nullable field)
        if self.guest_type is not None:
            field_value_map["guest_type"] = self.guest_type

        res = dynamo_client.update(
            USER_TABLE_NAME,
            key_expression,
            field_value_map,
        )

        # TODO: Parse res for errors as str
        return None


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

    # NOTE: This only works for 1mb of data atm (need to add logic for pagination)
    def get_all_of_col(self, table_name, col_name):
        deserializer = TypeDeserializer()
        response = self.client.scan(TableName=table_name, ProjectionExpression=col_name)
        return [
            {k: deserializer.deserialize(v) for k, v in item.items()}
            for item in response["Items"]
        ]

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
        dynamoValue = (
            str(field_value)
            if isinstance(field_value, int) or isinstance(field_value, float)
            else field_value
        )
        if dynamoType == "BOOL":
            dynamoValue = dynamoValue == "True"

        return {field_name: {dynamoType: dynamoValue}}

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

        if not api_key or api_key != INTERNAL_API_KEY:
            return Response(
                status_code=401,
                content_type="application/json",
                body={"message": "no valid api key"},
            )

        return func(*args, **kwargs)

    return wrapper


@app.get("/gizmo/ping")
def ping():
    return Response(
        status_code=200,
        content_type="application/json",
        body={"message": "ping success"},
    )


@app.get("/gizmo/user")
def login():
    try:
        user = User.from_first_last_db(
            app.current_event.headers.get("x-first-last"), CW_DYNAMO_CLIENT
        )
    except Exception as e:
        err_msg = "failed to fetch user from db"
        log.exception(err_msg)
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": err_msg},
        )

    if not user:
        err_msg = "no such user exists in db"
        log.info(err_msg)
        return Response(
            status_code=404,
            content_type="application/json",
            body={"message": err_msg},
        )
    return Response(
        status_code=200,
        content_type="application/json",
        body={
            "message": "login success",
            "user": user.as_map(),
        },
    )


@app.get("/gizmo/user/list")
@validate_internal_route
def list_users():
    try:
        users = User.list_db(CW_DYNAMO_CLIENT)

    except Exception as e:
        err_msg = "failed to list users from db"
        log.exception(err_msg)
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": err_msg},
        )

    user_maps = []
    for user in users:
        user_maps.append(user.as_map())

    return Response(
        status_code=200,
        content_type="application/json",
        body={
            "message": "list users success",
            "users": user_maps,
        },
    )


@app.get("/gizmo/user/guest")
def get_user_by_guest_link():
    guest_link = app.current_event.get_query_string_value("code", "")
    if not guest_link:
        return Response(
            status_code=400,
            content_type="application/json",
            body={"message": "no guest code provided in query param"},
        )

    try:
        user = User.from_guest_link_db(guest_link, CW_DYNAMO_CLIENT)
    except Exception as e:
        err_msg = "failed to fetch user from db"
        log.exception(err_msg)
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": err_msg},
        )

    if not user:
        err_msg = "no such user exists in db"
        log.warn(err_msg)
        return Response(
            status_code=404,
            content_type="application/json",
            body={"message": err_msg},
        )

    log.append_keys(user=user.__repr__())
    log.info("success retrieving user from guest link")
    return Response(
        status_code=200,
        content_type="application/json",
        body={
            "message": "guest lookup success",
            "user": user.as_map(),
        },
    )


@app.post("/gizmo/user")
def register():
    rsvps = app.current_event.json_body

    # If a guest link is included, we need to verify it and
    # link the associated user.
    our_actual_friend = None
    guest_link = rsvps[0].get("guestCode")
    if guest_link:
        log.append_keys(guest_link=guest_link)
        log.info("handling guest registration")
        try:
            log.info(f"looking up our actual friend with guest code {guest_link}")
            our_actual_friend = User.from_guest_link_db(guest_link, CW_DYNAMO_CLIENT)
            if our_actual_friend:
                log.append_keys(our_actual_friend=our_actual_friend.as_map())
                log.info("found our friend")

            # attach the real friend to their guest
            rsvps[0]["pairFirstLast"] = (
                our_actual_friend.first + "_" + our_actual_friend.last
            )
        except Exception as e:
            log.exception("failed lookup of our actual friend")
            return Response(
                status_code=500,
                content_type="application/json",
                body={"message": "failed lookup of our actual friend"},
            )

    # NOTE: Due to "Closed Plus Ones", we might get more than one rsvp as
    #       users with a "Closed Plus One" will fill out two rsvps at once.
    users = User.extract_users_from_rsvps(rsvps)

    # register user(s) in db
    log_users = []
    for user in users:
        try:
            user.register_db(CW_DYNAMO_CLIENT)
            log_users.append(user.as_map())
        except Exception as e:
            err_msg = "failed to register user in db"
            log.append_keys(failed_user=user.first)
            log.exception(err_msg)
            return Response(
                status_code=500,
                content_type="application/json",
                body={"message": err_msg},
            )
    log.append_keys(users=log_users)
    log.info("succeeded registering user in db")

    if guest_link:
        try:
            # link our friend to the new account made from their guest link
            our_actual_friend.guest_details.pair_first_last = (
                users[0].first.lower() + "_" + users[0].last.lower()
            )
            our_actual_friend.update_db(CW_DYNAMO_CLIENT)
        except Exception as e:
            log.exception("failed updating guest_first_last of our actual friend")
            return Response(
                status_code=500,
                content_type="application/json",
                body={"message": "failed lookup of our actual friend"},
            )

    # tether users if two are included
    if len(users) == 2:
        users[0].guest_details.pair_first_last = users[1].first + "_" + users[1].last
        users[1].guest_details.pair_first_last = users[0].first + "_" + users[0].last

    # notify user(s) of registration success
    for user in users:
        try:
            email_registration_success(user=user)
        except Exception as e:
            err_msg = "failed to send user registration success email"
            log.exception(err_msg)
        try:
            text_registration_success(user, inviter=our_actual_friend)
        except Exception as e:
            err_msg = "failed to send user registration success text"
            log.exception(err_msg)

    users_registered = [user.as_map() for user in users]
    return Response(
        status_code=200,
        content_type="application/json",
        body={"message": "success", "users": users_registered},
    )


@app.patch("/gizmo/user")
def update():
    user = User.extract_users_from_rsvps(app.current_event.json_body)[0]

    err = None
    try:
        err = user.update_db(CW_DYNAMO_CLIENT)
    except Exception as e:
        # damn
        err_msg = "failed to update user in db"
        log.exception(err_msg)
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": err_msg, "error": str(e)},
        )
    if err:
        log.append_keys(dynamo_err=err)
        log.error("encountered error updating user in dynamo")
        return Response(
            status_code=400,
            content_type="application/json",
            body={"message": err},
        )
    log.append_keys(user=user.__repr__())
    log.info("succeeded updating user in db")

    return Response(
        status_code=200,
        content_type="application/json",
        body={"message": "success", "user": user.as_map()},
    )


@app.post("/gizmo/email")
@validate_internal_route
def send_email():
    payload = app.current_event.json_body
    res = DOT_LOVE_MESSAGE_CLIENT.email(
        message_type=payload["template_type"],
        template_input=payload["template_details"],
        recipient_email=payload["recipient_email"],
    )
    return Response(
        status_code=200,
        content_type="application/json",
        body={"message": "email sent successfully", "data": res},
    )


@app.post("/gizmo/text")
def send_text():
    payload = app.current_event.json_body

    # handle text blasts
    is_blast = payload["is_blast"]
    if is_blast:
        numbers_dynamo_res = CW_DYNAMO_CLIENT.get_all_of_col(
            table_name=USER_TABLE_NAME, col_name="phone"
        )
        numbers = []
        for dynamo_res in numbers_dynamo_res:
            numbers.append(dynamo_res["phone"])

        res = DOT_LOVE_MESSAGE_CLIENT.text_blast(
            message_type=payload["template_type"],
            template_input=payload["template_details"],
            numbers=numbers,
        )
        return Response(
            status_code=200,
            content_type="application/json",
            body={"message": "text blast sent successfully", "data": res},
        )

    # NOTE: this is important for calls from Spectaculo, where the number is not known
    # fetch the phone number if not provided
    phone = payload["recipient_phone"]
    if phone == "" or phone == None:
        try:
            user = User.from_first_last_db(payload["first_last"], CW_DYNAMO_CLIENT)
        except Exception as e:
            err_msg = "failed to fetch user from db"
            log.exception(err_msg)
            return Response(
                status_code=500,
                content_type="application/json",
                body={"message": err_msg},
            )
        if not user:
            err_msg = "no such user exists in db"
            log.info(err_msg)
            return Response(
                status_code=404,
                content_type="application/json",
                body={"message": err_msg},
            )

        phone = user.address.phone

    res = DOT_LOVE_MESSAGE_CLIENT.text(
        message_type=payload["template_type"],
        template_input=payload["template_details"],
        recipient_phone=phone,
    )
    return Response(
        status_code=200,
        content_type="application/json",
        body={"message": "text sent successfully", "data": res},
    )


@app.post("/gizmo/survey")
def submit_survey():
    """
    Submit survey results for a user.

    Request body:
    {
        "responses": {
            "question1": "answer1",
            "question2": true,
            "question3": "written response"
        }
    }

    Uses X-First-Last header for user identification.
    """
    try:
        first_last = app.current_event.headers.get("x-first-last")
        if not first_last:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "Missing X-First-Last header"},
            )

        payload = app.current_event.json_body
        responses = payload.get("responses")

        if not responses:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "Missing responses field"},
            )

        # Store survey results in DynamoDB
        survey_item = {
            "first_last": {"S": first_last},
            "responses": {"S": json.dumps(responses)},
            "submitted_at": {"S": str(uuid.uuid4())},  # Using uuid as timestamp placeholder
        }

        CW_DYNAMO_CLIENT.client.put_item(
            TableName=SURVEY_RESULTS_TABLE_NAME,
            Item=survey_item
        )

        log.info(f"Survey submitted successfully for {first_last}")
        return Response(
            status_code=200,
            content_type="application/json",
            body={"message": "Survey submitted successfully"},
        )

    except Exception as e:
        log.exception("Failed to submit survey")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to submit survey", "error": str(e)},
        )


@app.get("/gizmo/survey")
def get_survey():
    """
    Get survey results for a user.
    Uses X-First-Last header for user identification.
    """
    try:
        first_last = app.current_event.headers.get("x-first-last")
        if not first_last:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "Missing X-First-Last header"},
            )

        result = CW_DYNAMO_CLIENT.client.get_item(
            TableName=SURVEY_RESULTS_TABLE_NAME,
            Key={"first_last": {"S": first_last}}
        )

        if "Item" not in result:
            return Response(
                status_code=404,
                content_type="application/json",
                body={"message": "No survey found for this user"},
            )

        responses = json.loads(result["Item"]["responses"]["S"])
        return Response(
            status_code=200,
            content_type="application/json",
            body={"message": "Survey found", "responses": responses},
        )

    except Exception as e:
        log.exception("Failed to get survey")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to get survey", "error": str(e)},
        )


@app.get("/gizmo/survey/all")
@validate_internal_route
def get_all_surveys():
    """
    Get all survey results (admin only).
    Requires Internal-Api-Key header.
    """
    try:
        results = CW_DYNAMO_CLIENT.get_all(SURVEY_RESULTS_TABLE_NAME)

        surveys = []
        for item in results:
            surveys.append({
                "first_last": item["first_last"]["S"],
                "responses": json.loads(item["responses"]["S"]),
            })

        return Response(
            status_code=200,
            content_type="application/json",
            body={"message": "All surveys retrieved", "surveys": surveys},
        )

    except Exception as e:
        log.exception("Failed to get all surveys")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to get all surveys", "error": str(e)},
        )


@app.post("/gizmo/text/cohort")
@validate_internal_route
def send_cohort_text():
    """
    Send text messages to a cohort of users based on a filter.

    Request body (simple):
    {
        "filter_field": "first" or "diet.meat" or "rsvp_status" etc,
        "filter_value": "tom" or "false" or "ATTENDING" etc,
        "message": "Your custom message here"
    }

    OR use template directly:
    {
        "filter_field": "rsvp_status",
        "filter_value": "ATTENDING",
        "template_type": "RAW_TEXT",
        "template_details": {"raw": "Your message"}
    }
    """
    try:
        payload = app.current_event.json_body
        filter_field = payload.get("filter_field")
        filter_value = payload.get("filter_value")

        # Support simple "message" field OR template_type/template_details
        simple_message = payload.get("message")
        template_type = payload.get("template_type")
        template_details = payload.get("template_details")

        if not filter_field or not filter_value:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "Missing required fields: filter_field, filter_value"},
            )

        # If simple message is provided, use RAW_TEXT template
        if simple_message:
            template_type = "RAW_TEXT"
            template_details = {"raw": simple_message}
        elif not template_type or not template_details:
            return Response(
                status_code=400,
                content_type="application/json",
                body={"message": "Must provide either 'message' or both 'template_type' and 'template_details'"},
            )

        # Get all users
        all_users = User.list_db(CW_DYNAMO_CLIENT)
        if not all_users:
            return Response(
                status_code=404,
                content_type="application/json",
                body={"message": "No users found in database"},
            )

        # Filter users based on the field and value
        filtered_users = []
        for user in all_users:
            user_map = user.as_map()

            # Navigate nested fields (e.g., "diet.meat" -> check user_map["diet"]["meat"])
            field_parts = filter_field.split(".")
            current_value = user_map

            try:
                for part in field_parts:
                    current_value = current_value[part]

                # Convert both to strings for comparison
                if str(current_value).lower() == str(filter_value).lower():
                    filtered_users.append(user)
            except (KeyError, TypeError):
                # Field doesn't exist or can't navigate - skip this user
                continue

        if not filtered_users:
            return Response(
                status_code=200,
                content_type="application/json",
                body={
                    "message": f"No users matched filter {filter_field}={filter_value}",
                    "matched_count": 0,
                    "users_checked": len(all_users)
                },
            )

        # Send texts to filtered users
        numbers = [user.address.phone for user in filtered_users if user.address.phone]

        if not numbers:
            return Response(
                status_code=200,
                content_type="application/json",
                body={
                    "message": "No valid phone numbers found for matched users",
                    "matched_count": len(filtered_users),
                    "phone_numbers_found": 0
                },
            )

        res = DOT_LOVE_MESSAGE_CLIENT.text_blast(
            message_type=template_type,
            template_input=template_details,
            numbers=numbers,
        )

        return Response(
            status_code=200,
            content_type="application/json",
            body={
                "message": f"Cohort text sent successfully to {len(numbers)} users",
                "filter_field": filter_field,
                "filter_value": filter_value,
                "matched_count": len(filtered_users),
                "texts_sent": len(numbers),
                "data": res
            },
        )

    except Exception as e:
        log.exception("Failed to send cohort text")
        return Response(
            status_code=500,
            content_type="application/json",
            body={"message": "Failed to send cohort text", "error": str(e)},
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
    # Exclude middleware for healthcheck
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
    # TODO: DO NOT USE THIS - IT PERSISTS ACROSS INVOCATIONS
    app.append_context(first_last=first_last)

    return handler(event, context)


@log.inject_lambda_context(log_event=True)
@middleware_before
def handler(event, context):
    try:
        return app.resolve(event, context)
    except Exception as e:
        log.exception("unhandled server error encountered")
        return {
            "code": 500,
            "message": "Unhandled server error encountered",
        }


# NOTE: Doing this at the top level so the client connections are preserved b/t lambda calls
# Initialize clients
CW_DYNAMO_CLIENT = CWDynamoClient()
TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
SES_CLIENT = boto3.client("ses")
DOT_LOVE_MESSAGE_CLIENT = DotLoveMessageClient(
    SES_CLIENT, SES_SENDER_EMAIL, SES_CONFIG_ID
)
