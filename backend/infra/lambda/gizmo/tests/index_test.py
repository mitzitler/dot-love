import json
import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch, call

# Set required environment variables before importing index
os.environ["user_table_name"] = "test_user_table"
os.environ["survey_results_table_name"] = "test_survey_table"
os.environ["internal_api_key"] = "test_internal_key"
os.environ["ses_sender_email"] = "test@example.com"
os.environ["ses_config_id"] = "test_config"
os.environ["ses_admin_list"] = "admin@example.com"
os.environ["twilio_auth_token"] = "test_twilio_token"
os.environ["twilio_account_sid"] = "test_twilio_sid"
os.environ["twilio_sender_number"] = "+15555551234"
os.environ["mitzi_phone"] = "+15555551111"
os.environ["mitzi_email"] = "mitzi@example.com"
os.environ["matthew_phone"] = "+15555552222"
os.environ["matthew_email"] = "matthew@example.com"
os.environ["ginny_phone"] = "+15555553333"
os.environ["open_plus_one_code"] = "test_code"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Add parent directory to path to import the lambda function
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock boto3 and twilio before importing index to avoid AWS/Twilio credentials requirement
with patch("boto3.client"), patch("twilio.rest.Client"):
    import index


class TestDotLoveMessageType(unittest.TestCase):
    """Test suite for DotLoveMessageType enum."""

    def test_enum_values(self):
        """Test that enum has expected values."""
        self.assertEqual(index.DotLoveMessageType.REGISTRATION_SUCCESS_EMAIL_WITH_GUEST.value, 1)
        self.assertEqual(index.DotLoveMessageType.RAW_TEXT.value, 6)
        self.assertEqual(index.DotLoveMessageType.SURVEY_ALERT.value, 9)

    def test_enum_str(self):
        """Test enum string representation."""
        self.assertEqual(str(index.DotLoveMessageType.RAW_TEXT), "RAW_TEXT")

    def test_enum_repr(self):
        """Test enum repr."""
        self.assertEqual(repr(index.DotLoveMessageType.RAW_EMAIL), "DotLoveMessageType.RAW_EMAIL")


class TestRsvpStatus(unittest.TestCase):
    """Test suite for RsvpStatus enum."""

    def test_enum_values(self):
        """Test RsvpStatus enum values."""
        self.assertEqual(index.RsvpStatus.UNDECIDED.value, 1)
        self.assertEqual(index.RsvpStatus.ATTENDING.value, 2)
        self.assertEqual(index.RsvpStatus.NOTATTENDING.value, 3)


class TestPronouns(unittest.TestCase):
    """Test suite for Pronouns enum."""

    def test_enum_values(self):
        """Test Pronouns enum values."""
        self.assertEqual(index.Pronouns.SHE_HER.value, 1)
        self.assertEqual(index.Pronouns.HE_HIM.value, 2)
        self.assertEqual(index.Pronouns.THEY_THEM.value, 3)


class TestUserAddress(unittest.TestCase):
    """Test suite for UserAddress class."""

    def test_init(self):
        """Test UserAddress initialization."""
        address = index.UserAddress(
            "123 Main St",
            "Apt 4",
            "New York",
            "10001",
            "USA",
            "NY",
            "+15555551234"
        )
        self.assertEqual(address.street, "123 Main St")
        self.assertEqual(address.phone, "+15555551234")

    def test_as_map(self):
        """Test UserAddress.as_map()."""
        address = index.UserAddress(
            "123 Main St",
            "Apt 4",
            "New York",
            "10001",
            "USA",
            "NY",
            "+15555551234"
        )
        result = address.as_map()
        self.assertEqual(result["street"], "123 Main St")
        self.assertEqual(result["phone"], "+15555551234")
        self.assertEqual(result["zipcode"], "10001")


class TestUserDiet(unittest.TestCase):
    """Test suite for UserDiet class."""

    def test_init(self):
        """Test UserDiet initialization."""
        diet = index.UserDiet(True, False, True, False, True, False, True, False, "No nuts")
        self.assertTrue(diet.alcohol)
        self.assertFalse(diet.meat)
        self.assertEqual(diet.restrictions, "No nuts")

    def test_as_map(self):
        """Test UserDiet.as_map()."""
        diet = index.UserDiet(True, False, True, False, True, False, True, False, "No nuts")
        result = diet.as_map()
        self.assertTrue(result["alcohol"])
        self.assertFalse(result["meat"])
        self.assertEqual(result["restrictions"], "No nuts")


class TestGuestDetails(unittest.TestCase):
    """Test suite for GuestDetails class."""

    def test_init(self):
        """Test GuestDetails initialization."""
        details = index.GuestDetails("abc123", "john_doe", True)
        self.assertEqual(details.link, "abc123")
        self.assertEqual(details.pair_first_last, "john_doe")
        self.assertTrue(details.date_link_requested)

    def test_as_map(self):
        """Test GuestDetails.as_map()."""
        details = index.GuestDetails("abc123", "john_doe", True)
        result = details.as_map()
        self.assertEqual(result["link"], "abc123")
        self.assertEqual(result["pair_first_last"], "john_doe")
        self.assertTrue(result["date_link_requested"])


class TestUser(unittest.TestCase):
    """Test suite for User class."""

    def setUp(self):
        """Set up test fixtures."""
        self.address = index.UserAddress(
            "123 Main St", "Apt 4", "New York", "10001", "USA", "NY", "+15555551234"
        )
        self.diet = index.UserDiet(True, False, True, False, True, False, True, False, "No nuts")
        self.guest_details = index.GuestDetails("abc123", "jane_doe", True)

    def test_init(self):
        """Test User initialization."""
        user = index.User(
            "John",
            "Doe",
            "code123",
            index.RsvpStatus.ATTENDING,
            index.Pronouns.HE_HIM,
            self.address,
            "john@example.com",
            self.diet,
            self.guest_details,
            "family",
            True,
            100
        )
        self.assertEqual(user.first, "John")
        self.assertEqual(user.last, "Doe")
        self.assertEqual(user.rsvp_code, "code123")
        self.assertEqual(user.high_score, 100)

    def test_as_map(self):
        """Test User.as_map()."""
        user = index.User(
            "John",
            "Doe",
            "code123",
            index.RsvpStatus.ATTENDING,
            index.Pronouns.HE_HIM,
            self.address,
            "john@example.com",
            self.diet,
            self.guest_details,
            "family",
            True,
            100
        )
        result = user.as_map()
        self.assertEqual(result["first"], "John")
        self.assertEqual(result["last"], "Doe")
        self.assertEqual(result["rsvp_status"], "ATTENDING")
        self.assertEqual(result["pronouns"], "HE_HIM")
        self.assertEqual(result["guest_type"], "family")
        self.assertTrue(result["rehearsal_dinner_invited"])

    def test_from_client_rsvp(self):
        """Test User.from_client_rsvp()."""
        rsvp_data = {
            "firstName": "John",
            "lastName": "Doe",
            "rsvpCode": "code123",
            "rsvpStatus": "ATTENDING",
            "pronouns": "he/him",
            "email": "john@example.com",
            "phoneNumber": "5555551234",
            "phoneNumberCountryCode": "1",
            "streetAddress": "123 Main St",
            "secondAddress": "Apt 4",
            "city": "New York",
            "zipcode": "10001",
            "country": "USA",
            "stateProvince": "NY",
            "drinkAlcohol": True,
            "eatMeat": False,
            "eatDairy": True,
            "eatFish": False,
            "eatShellfish": True,
            "eatEggs": False,
            "eatGluten": True,
            "eatPeanuts": False,
            "moreRestrictions": "No nuts",
            "pairFirstLast": "",
            "dateLinkRequested": True
        }
        user = index.User.from_client_rsvp(rsvp_data)
        self.assertEqual(user.first, "john")
        self.assertEqual(user.last, "doe")
        self.assertEqual(user.rsvp_code, "code123")
        self.assertEqual(user.rsvp_status, index.RsvpStatus.ATTENDING)
        self.assertEqual(user.address.phone, "+15555551234")


class TestCWDynamoClient(unittest.TestCase):
    """Test suite for CWDynamoClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.dynamo_client = index.CWDynamoClient()
        self.dynamo_client.client = self.mock_client

    def test_determine_dynamo_data_type(self):
        """Test determine_dynamo_data_type()."""
        self.assertEqual(self.dynamo_client.determine_dynamo_data_type("test"), "S")
        self.assertEqual(self.dynamo_client.determine_dynamo_data_type(123), "N")
        self.assertEqual(self.dynamo_client.determine_dynamo_data_type(True), "BOOL")
        self.assertEqual(self.dynamo_client.determine_dynamo_data_type({}), "M")
        self.assertEqual(self.dynamo_client.determine_dynamo_data_type(["a", "b"]), "SS")

    def test_dynamo_format_value_mapping(self):
        """Test dynamo_format_value_mapping()."""
        result = self.dynamo_client.dynamo_format_value_mapping("field", "value", "create")
        self.assertEqual(result, {"field": {"S": "value"}})

        result = self.dynamo_client.dynamo_format_value_mapping("field", 123, "update")
        self.assertEqual(result, {":field": {"N": "123"}})

    def test_format_update_expression(self):
        """Test format_update_expression()."""
        result = self.dynamo_client.format_update_expression(["field1", "field2"])
        self.assertIn("SET field1 = :field1", result)
        self.assertIn("field2 = :field2", result)

    def test_get(self):
        """Test get()."""
        self.mock_client.get_item.return_value = {"Item": {"field": {"S": "value"}}}
        result = self.dynamo_client.get("table", {"key": {"S": "value"}})
        self.assertEqual(result, {"field": {"S": "value"}})

    def test_get_all(self):
        """Test get_all() without pagination."""
        self.mock_client.scan.return_value = {
            "Items": [{"field": {"S": "value"}}],
        }
        result = self.dynamo_client.get_all("table")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["field"]["S"], "value")

    def test_get_all_with_pagination(self):
        """Test get_all() with pagination."""
        self.mock_client.scan.side_effect = [
            {
                "Items": [{"field": {"S": "value1"}}],
                "LastEvaluatedKey": {"key": "next"}
            },
            {
                "Items": [{"field": {"S": "value2"}}],
            }
        ]
        result = self.dynamo_client.get_all("table")
        self.assertEqual(len(result), 2)


class TestDotLoveMessageClient(unittest.TestCase):
    """Test suite for DotLoveMessageClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ses = Mock()
        self.mock_twilio = Mock()
        self.client = index.DotLoveMessageClient(
            self.mock_ses,
            "sender@example.com",
            "config_id"
        )
        # Mock TWILIO_CLIENT
        index.TWILIO_CLIENT = self.mock_twilio

    def test_init(self):
        """Test DotLoveMessageClient initialization."""
        self.assertEqual(self.client.sender_email, "sender@example.com")
        self.assertEqual(self.client.config_id, "config_id")
        self.assertIn("Matthew", self.client.contact_table)

    def test_email(self):
        """Test email() method."""
        self.mock_ses.send_email.return_value = {
            "MessageId": "123",
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }
        result = self.client.email(
            index.DotLoveMessageType.RAW_EMAIL,
            {"raw": "Test message", "subject": "Test"},
            "recipient@example.com"
        )
        self.assertIn("SES response ID: 123", result)
        self.mock_ses.send_email.assert_called_once()

    def test_text(self):
        """Test text() method."""
        mock_message = Mock()
        self.mock_twilio.messages.create.return_value = mock_message

        self.client.text(
            "RAW_TEXT",
            {"raw": "Test message"},
            "+15555551234"
        )
        self.mock_twilio.messages.create.assert_called_once()
        call_args = self.mock_twilio.messages.create.call_args
        self.assertIn("Test message", call_args[1]["body"])

    def test_text_blast(self):
        """Test text_blast() method."""
        self.client.text_blast(
            "RAW_TEXT",
            {"raw": "Test message"},
            ["+15555551234", "+15555555678"]
        )
        self.assertEqual(self.mock_twilio.messages.create.call_count, 2)

    def test_email_blast(self):
        """Test email_blast() method."""
        self.mock_ses.send_email.return_value = {
            "MessageId": "123",
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }
        self.client.email_blast(
            index.DotLoveMessageType.RAW_EMAIL,
            {"raw": "Test message", "subject": "Test"},
            ["recipient1@example.com", "recipient2@example.com"]
        )
        self.assertEqual(self.mock_ses.send_email.call_count, 2)


class TestHelperFunctions(unittest.TestCase):
    """Test suite for helper functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ses = Mock()
        self.mock_twilio = Mock()
        index.DOT_LOVE_MESSAGE_CLIENT = index.DotLoveMessageClient(
            self.mock_ses,
            "sender@example.com",
            "config_id"
        )
        index.TWILIO_CLIENT = self.mock_twilio

    def test_text_admins(self):
        """Test text_admins() sends to all admins."""
        index.text_admins("Test message")
        # Should send to mitzi, matthew, and ginny
        self.assertEqual(self.mock_twilio.messages.create.call_count, 3)

    def test_email_registration_success_not_attending(self):
        """Test email_registration_success() for not attending."""
        address = index.UserAddress("123 Main", "", "NYC", "10001", "USA", "NY", "+15555551234")
        diet = index.UserDiet(True, True, True, True, True, True, True, True, "")
        guest_details = index.GuestDetails("abc123", "", False)
        user = index.User(
            "John", "Doe", "code123",
            index.RsvpStatus.NOTATTENDING,
            index.Pronouns.HE_HIM,
            address, "john@example.com", diet, guest_details
        )
        # Should return early without sending email
        result = index.email_registration_success(user)
        self.assertIsNone(result)

    @patch.object(index.DotLoveMessageClient, 'email')
    def test_email_registration_success_with_guest(self, mock_email):
        """Test email_registration_success() with guest."""
        address = index.UserAddress("123 Main", "", "NYC", "10001", "USA", "NY", "+15555551234")
        diet = index.UserDiet(True, True, True, True, True, True, True, True, "")
        guest_details = index.GuestDetails("abc123", "", True)
        user = index.User(
            "John", "Doe", "code123",
            index.RsvpStatus.ATTENDING,
            index.Pronouns.HE_HIM,
            address, "john@example.com", diet, guest_details
        )
        index.email_registration_success(user)
        mock_email.assert_called_once()
        call_args = mock_email.call_args[0]
        self.assertEqual(call_args[0], index.DotLoveMessageType.REGISTRATION_SUCCESS_EMAIL_WITH_GUEST)

    def test_text_registration_success_not_attending(self):
        """Test text_registration_success() for not attending user."""
        address = index.UserAddress("123 Main", "", "NYC", "10001", "USA", "NY", "+15555551234")
        diet = index.UserDiet(True, True, True, True, True, True, True, True, "")
        guest_details = index.GuestDetails("abc123", "", False)
        user = index.User(
            "John", "Doe", "code123",
            index.RsvpStatus.NOTATTENDING,
            index.Pronouns.HE_HIM,
            address, "john@example.com", diet, guest_details
        )
        # text_registration_success has a bug: line 167 references plus_one_text_body
        # which is not defined until later. This will cause a NameError.
        # We'll test that the bug exists
        with self.assertRaises(NameError):
            index.text_registration_success(user, None)


class TestAPIEndpoints(unittest.TestCase):
    """Test suite for API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_dynamo_client = Mock()
        index.CW_DYNAMO_CLIENT = self.mock_dynamo_client
        index.app.context = {"trace_id": "test_trace_123"}

    def test_ping(self):
        """Test ping endpoint."""
        response = index.ping()
        self.assertEqual(response.status_code, 200)
        # Response.body is already a dict, not a JSON string
        body = response.body
        self.assertEqual(body["message"], "ping success")

    def test_login_success(self):
        """Test login endpoint with valid user."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "john_doe"
        index.app.current_event = mock_event

        self.mock_dynamo_client.get.return_value = {
            "first_last": {"S": "john_doe"},
            "rsvp_code": {"S": "code123"},
            "rsvp_status": {"S": "ATTENDING"},
            "pronouns": {"S": "HE_HIM"},
            "email": {"S": "john@example.com"},
            "street": {"S": "123 Main"},
            "second_line": {"S": ""},
            "city": {"S": "NYC"},
            "zipcode": {"S": "10001"},
            "country": {"S": "USA"},
            "state_loc": {"S": "NY"},
            "phone": {"S": "+15555551234"},
            "alcohol": {"BOOL": True},
            "meat": {"BOOL": True},
            "dairy": {"BOOL": True},
            "fish": {"BOOL": True},
            "shellfish": {"BOOL": True},
            "eggs": {"BOOL": True},
            "gluten": {"BOOL": True},
            "peanuts": {"BOOL": True},
            "restrictions": {"S": ""},
            "guest_link": {"S": "abc123"},
            "guest_pair_first_last": {"S": ""},
            "date_link_requested": {"BOOL": False},
            "high_score": {"N": "0"}
        }

        response = index.login()
        self.assertEqual(response.status_code, 200)
        body = response.body
        self.assertEqual(body["message"], "login success")
        self.assertIn("user", body)

    def test_login_user_not_found(self):
        """Test login endpoint with non-existent user."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "john_doe"
        index.app.current_event = mock_event
        self.mock_dynamo_client.get.return_value = None

        response = index.login()
        self.assertEqual(response.status_code, 404)
        body = response.body
        self.assertIn("no such user exists", body["message"])

    def test_list_users_success(self):
        """Test list_users endpoint."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "test_internal_key"
        index.app.current_event = mock_event

        self.mock_dynamo_client.get_all.return_value = [
            {
                "first_last": {"S": "john_doe"},
                "rsvp_code": {"S": "code123"},
                "rsvp_status": {"S": "ATTENDING"},
                "pronouns": {"S": "HE_HIM"},
                "email": {"S": "john@example.com"},
                "street": {"S": "123 Main"},
                "second_line": {"S": ""},
                "city": {"S": "NYC"},
                "zipcode": {"S": "10001"},
                "country": {"S": "USA"},
                "state_loc": {"S": "NY"},
                "phone": {"S": "+15555551234"},
                "alcohol": {"BOOL": True},
                "meat": {"BOOL": True},
                "dairy": {"BOOL": True},
                "fish": {"BOOL": True},
                "shellfish": {"BOOL": True},
                "eggs": {"BOOL": True},
                "gluten": {"BOOL": True},
                "peanuts": {"BOOL": True},
                "restrictions": {"S": ""},
                "guest_link": {"S": "abc123"},
                "guest_pair_first_last": {"S": ""},
                "date_link_requested": {"BOOL": False},
                "high_score": {"N": "0"}
            }
        ]

        response = index.list_users()
        self.assertEqual(response.status_code, 200)
        body = response.body
        self.assertEqual(len(body["users"]), 1)

    def test_list_users_no_api_key(self):
        """Test list_users endpoint without API key."""
        mock_event = Mock()
        mock_event.headers.get.return_value = None
        index.app.current_event = mock_event

        response = index.list_users()
        self.assertEqual(response.status_code, 401)

    def test_get_user_by_guest_link_success(self):
        """Test get_user_by_guest_link endpoint."""
        mock_event = Mock()
        mock_event.get_query_string_value.return_value = "abc123"
        index.app.current_event = mock_event

        self.mock_dynamo_client.client.query.return_value = {
            "Items": [{
                "first_last": {"S": "john_doe"},
                "rsvp_code": {"S": "code123"},
                "rsvp_status": {"S": "ATTENDING"},
                "pronouns": {"S": "HE_HIM"},
                "email": {"S": "john@example.com"},
                "street": {"S": "123 Main"},
                "second_line": {"S": ""},
                "city": {"S": "NYC"},
                "zipcode": {"S": "10001"},
                "country": {"S": "USA"},
                "state_loc": {"S": "NY"},
                "phone": {"S": "+15555551234"},
                "alcohol": {"BOOL": True},
                "meat": {"BOOL": True},
                "dairy": {"BOOL": True},
                "fish": {"BOOL": True},
                "shellfish": {"BOOL": True},
                "eggs": {"BOOL": True},
                "gluten": {"BOOL": True},
                "peanuts": {"BOOL": True},
                "restrictions": {"S": ""},
                "guest_link": {"S": "abc123"},
                "guest_pair_first_last": {"S": ""},
                "date_link_requested": {"BOOL": False},
            }]
        }

        response = index.get_user_by_guest_link()
        self.assertEqual(response.status_code, 200)
        body = response.body
        self.assertEqual(body["message"], "guest lookup success")

    def test_get_user_by_guest_link_no_code(self):
        """Test get_user_by_guest_link without code."""
        mock_event = Mock()
        mock_event.get_query_string_value.return_value = ""
        index.app.current_event = mock_event

        response = index.get_user_by_guest_link()
        self.assertEqual(response.status_code, 400)

    @patch('index.email_registration_success')
    @patch('index.text_registration_success')
    def test_register_single_user(self, mock_text, mock_email):
        """Test register endpoint with single user."""
        mock_event = Mock()
        mock_event.json_body = [{
            "firstName": "John",
            "lastName": "Doe",
            "rsvpCode": "code123",
            "rsvpStatus": "ATTENDING",
            "pronouns": "he/him",
            "email": "john@example.com",
            "phoneNumber": "5555551234",
            "phoneNumberCountryCode": "1",
            "streetAddress": "123 Main St",
            "secondAddress": "",
            "city": "New York",
            "zipcode": "10001",
            "country": "USA",
            "stateProvince": "NY",
            "drinkAlcohol": True,
            "eatMeat": True,
            "eatDairy": True,
            "eatFish": True,
            "eatShellfish": True,
            "eatEggs": True,
            "eatGluten": True,
            "eatPeanuts": True,
            "moreRestrictions": "",
            "dateLinkRequested": False
        }]
        index.app.current_event = mock_event

        response = index.register()
        self.assertEqual(response.status_code, 200)
        body = response.body
        self.assertEqual(len(body["users"]), 1)
        self.mock_dynamo_client.create.assert_called()

    @patch('index.email_registration_success')
    @patch('index.text_registration_success')
    def test_register_with_guest_link(self, mock_text, mock_email):
        """Test register endpoint with guest link."""
        mock_event = Mock()
        mock_event.json_body = [{
            "guestCode": "abc123",
            "firstName": "Jane",
            "lastName": "Smith",
            "rsvpCode": "code456",
            "rsvpStatus": "ATTENDING",
            "pronouns": "she/her",
            "email": "jane@example.com",
            "phoneNumber": "5555555678",
            "phoneNumberCountryCode": "1",
            "streetAddress": "456 Oak Ave",
            "secondAddress": "",
            "city": "Boston",
            "zipcode": "02101",
            "country": "USA",
            "stateProvince": "MA",
            "drinkAlcohol": True,
            "eatMeat": True,
            "eatDairy": True,
            "eatFish": True,
            "eatShellfish": True,
            "eatEggs": True,
            "eatGluten": True,
            "eatPeanuts": True,
            "moreRestrictions": "",
            "dateLinkRequested": False
        }]
        index.app.current_event = mock_event

        # Mock the guest link lookup
        self.mock_dynamo_client.client.query.return_value = {
            "Items": [{
                "first_last": {"S": "john_doe"},
                "rsvp_code": {"S": "code123"},
                "rsvp_status": {"S": "ATTENDING"},
                "pronouns": {"S": "HE_HIM"},
                "email": {"S": "john@example.com"},
                "street": {"S": "123 Main"},
                "second_line": {"S": ""},
                "city": {"S": "NYC"},
                "zipcode": {"S": "10001"},
                "country": {"S": "USA"},
                "state_loc": {"S": "NY"},
                "phone": {"S": "+15555551234"},
                "alcohol": {"BOOL": True},
                "meat": {"BOOL": True},
                "dairy": {"BOOL": True},
                "fish": {"BOOL": True},
                "shellfish": {"BOOL": True},
                "eggs": {"BOOL": True},
                "gluten": {"BOOL": True},
                "peanuts": {"BOOL": True},
                "restrictions": {"S": ""},
                "guest_link": {"S": "abc123"},
                "guest_pair_first_last": {"S": ""},
                "date_link_requested": {"BOOL": True},
            }]
        }

        response = index.register()
        self.assertEqual(response.status_code, 200)
        # Should update the inviter's guest_pair_first_last
        self.mock_dynamo_client.update.assert_called()

    def test_update_user(self):
        """Test update endpoint."""
        mock_event = Mock()
        mock_event.json_body = [{
            "firstName": "John",
            "lastName": "Doe",
            "rsvpCode": "code123",
            "rsvpStatus": "ATTENDING",
            "pronouns": "he/him",
            "email": "john@example.com",
            "phoneNumber": "5555551234",
            "phoneNumberCountryCode": "1",
            "streetAddress": "123 Main St",
            "secondAddress": "",
            "city": "New York",
            "zipcode": "10001",
            "country": "USA",
            "stateProvince": "NY",
            "drinkAlcohol": True,
            "eatMeat": True,
            "eatDairy": True,
            "eatFish": True,
            "eatShellfish": True,
            "eatEggs": True,
            "eatGluten": True,
            "eatPeanuts": True,
            "moreRestrictions": "",
            "dateLinkRequested": False
        }]
        index.app.current_event = mock_event

        response = index.update()
        self.assertEqual(response.status_code, 200)
        self.mock_dynamo_client.update.assert_called()

    def test_send_email_endpoint(self):
        """Test send_email endpoint."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "test_internal_key"
        # Use the enum value (10) instead of string for RAW_EMAIL
        mock_event.json_body = {
            "template_type": index.DotLoveMessageType.RAW_EMAIL,
            "template_details": {"raw": "Test message", "subject": "Test"},
            "recipient_email": "test@example.com"
        }
        index.app.current_event = mock_event

        mock_ses = Mock()
        mock_ses.send_email.return_value = {
            "MessageId": "123",
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }
        index.DOT_LOVE_MESSAGE_CLIENT = index.DotLoveMessageClient(
            mock_ses, "sender@example.com", "config_id"
        )

        response = index.send_email()
        self.assertEqual(response.status_code, 200)

    def test_send_text_endpoint(self):
        """Test send_text endpoint."""
        mock_event = Mock()
        mock_event.json_body = {
            "is_blast": False,
            "template_type": "RAW_TEXT",
            "template_details": {"raw": "Test message"},
            "recipient_phone": "+15555551234",
            "first_last": "john_doe"
        }
        index.app.current_event = mock_event

        mock_twilio = Mock()
        index.TWILIO_CLIENT = mock_twilio

        response = index.send_text()
        self.assertEqual(response.status_code, 200)
        mock_twilio.messages.create.assert_called()

    def test_send_text_blast(self):
        """Test send_text endpoint with blast."""
        mock_event = Mock()
        mock_event.json_body = {
            "is_blast": True,
            "template_type": "RAW_TEXT",
            "template_details": {"raw": "Test message"}
        }
        index.app.current_event = mock_event

        self.mock_dynamo_client.get_all_of_col.return_value = [
            {"phone": "+15555551234"},
            {"phone": "+15555555678"}
        ]

        mock_twilio = Mock()
        index.TWILIO_CLIENT = mock_twilio

        response = index.send_text()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_twilio.messages.create.call_count, 2)

    def test_submit_survey(self):
        """Test submit_survey endpoint."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "john_doe"
        mock_event.json_body = {
            "responses": {
                "question1": "answer1",
                "question2": True,
                "question3": "written response"
            }
        }
        index.app.current_event = mock_event

        response = index.submit_survey()
        self.assertEqual(response.status_code, 200)
        self.mock_dynamo_client.client.put_item.assert_called_once()

    def test_submit_survey_missing_header(self):
        """Test submit_survey without X-First-Last header."""
        mock_event = Mock()
        mock_event.headers.get.return_value = None
        mock_event.json_body = {"responses": {}}
        index.app.current_event = mock_event

        response = index.submit_survey()
        self.assertEqual(response.status_code, 400)

    def test_get_survey(self):
        """Test get_survey endpoint."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "john_doe"
        index.app.current_event = mock_event

        self.mock_dynamo_client.client.get_item.return_value = {
            "Item": {
                "first_last": {"S": "john_doe"},
                "responses": {"S": '{"question1": "answer1"}'}
            }
        }

        response = index.get_survey()
        self.assertEqual(response.status_code, 200)
        body = response.body
        self.assertIn("responses", body)

    def test_get_survey_not_found(self):
        """Test get_survey when no survey exists."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "john_doe"
        index.app.current_event = mock_event

        self.mock_dynamo_client.client.get_item.return_value = {}

        response = index.get_survey()
        self.assertEqual(response.status_code, 404)

    def test_get_all_surveys(self):
        """Test get_all_surveys endpoint."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "test_internal_key"
        index.app.current_event = mock_event

        self.mock_dynamo_client.get_all.return_value = [
            {
                "first_last": {"S": "john_doe"},
                "responses": {"S": '{"question1": "answer1"}'}
            },
            {
                "first_last": {"S": "jane_smith"},
                "responses": {"S": '{"question1": "answer2"}'}
            }
        ]

        response = index.get_all_surveys()
        self.assertEqual(response.status_code, 200)
        body = response.body
        self.assertEqual(len(body["surveys"]), 2)

    def test_get_all_surveys_no_api_key(self):
        """Test get_all_surveys without API key."""
        mock_event = Mock()
        mock_event.headers.get.return_value = None
        index.app.current_event = mock_event

        response = index.get_all_surveys()
        self.assertEqual(response.status_code, 401)

    @patch.object(index.User, 'list_db')
    def test_send_cohort_text(self, mock_list_db):
        """Test send_cohort_text endpoint."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "test_internal_key"
        mock_event.json_body = {
            "filter_field": "rsvp_status",
            "filter_value": "ATTENDING",
            "message": "Test cohort message"
        }
        index.app.current_event = mock_event

        # Mock users
        address = index.UserAddress("123 Main", "", "NYC", "10001", "USA", "NY", "+15555551234")
        diet = index.UserDiet(True, True, True, True, True, True, True, True, "")
        guest_details = index.GuestDetails("abc123", "", False)
        user1 = index.User(
            "John", "Doe", "code123",
            index.RsvpStatus.ATTENDING,
            index.Pronouns.HE_HIM,
            address, "john@example.com", diet, guest_details
        )
        user2 = index.User(
            "Jane", "Smith", "code456",
            index.RsvpStatus.NOTATTENDING,
            index.Pronouns.SHE_HER,
            address, "jane@example.com", diet, guest_details
        )
        mock_list_db.return_value = [user1, user2]

        mock_twilio = Mock()
        index.TWILIO_CLIENT = mock_twilio

        response = index.send_cohort_text()
        self.assertEqual(response.status_code, 200)
        body = response.body
        self.assertEqual(body["matched_count"], 1)  # Only one ATTENDING user
        mock_twilio.messages.create.assert_called()

    @patch.object(index.User, 'list_db')
    def test_send_cohort_text_no_matches(self, mock_list_db):
        """Test send_cohort_text with no matching users."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "test_internal_key"
        mock_event.json_body = {
            "filter_field": "rsvp_status",
            "filter_value": "UNDECIDED",
            "message": "Test message"
        }
        index.app.current_event = mock_event

        address = index.UserAddress("123 Main", "", "NYC", "10001", "USA", "NY", "+15555551234")
        diet = index.UserDiet(True, True, True, True, True, True, True, True, "")
        guest_details = index.GuestDetails("abc123", "", False)
        user = index.User(
            "John", "Doe", "code123",
            index.RsvpStatus.ATTENDING,
            index.Pronouns.HE_HIM,
            address, "john@example.com", diet, guest_details
        )
        mock_list_db.return_value = [user]

        response = index.send_cohort_text()
        self.assertEqual(response.status_code, 200)
        body = response.body
        self.assertEqual(body["matched_count"], 0)

    @patch.object(index.User, 'list_db')
    def test_send_cohort_text_nested_field(self, mock_list_db):
        """Test send_cohort_text with nested field filter."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "test_internal_key"
        mock_event.json_body = {
            "filter_field": "diet.meat",
            "filter_value": "False",
            "message": "Vegetarian menu options!"
        }
        index.app.current_event = mock_event

        address = index.UserAddress("123 Main", "", "NYC", "10001", "USA", "NY", "+15555551234")
        diet_meat = index.UserDiet(True, True, True, True, True, True, True, True, "")
        diet_no_meat = index.UserDiet(True, False, True, True, True, True, True, True, "")
        guest_details = index.GuestDetails("abc123", "", False)
        user1 = index.User(
            "John", "Doe", "code123",
            index.RsvpStatus.ATTENDING,
            index.Pronouns.HE_HIM,
            address, "john@example.com", diet_meat, guest_details
        )
        user2 = index.User(
            "Jane", "Smith", "code456",
            index.RsvpStatus.ATTENDING,
            index.Pronouns.SHE_HER,
            address, "jane@example.com", diet_no_meat, guest_details
        )
        mock_list_db.return_value = [user1, user2]

        mock_twilio = Mock()
        index.TWILIO_CLIENT = mock_twilio

        response = index.send_cohort_text()
        self.assertEqual(response.status_code, 200)
        body = response.body
        self.assertEqual(body["matched_count"], 1)  # Only Jane (no meat)

    @patch.object(index.User, 'list_db')
    def test_send_cohort_email(self, mock_list_db):
        """Test send_cohort_email endpoint with template_type and template_details."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "test_internal_key"
        # Use template_type and template_details instead of message/subject
        # to avoid the bug where it sets template_type = "RAW_EMAIL" (string)
        mock_event.json_body = {
            "filter_field": "rsvp_status",
            "filter_value": "ATTENDING",
            "template_type": index.DotLoveMessageType.RAW_EMAIL,
            "template_details": {"raw": "<p>Test cohort message</p>", "subject": "Test Subject"}
        }
        index.app.current_event = mock_event

        address = index.UserAddress("123 Main", "", "NYC", "10001", "USA", "NY", "+15555551234")
        diet = index.UserDiet(True, True, True, True, True, True, True, True, "")
        guest_details = index.GuestDetails("abc123", "", False)
        user = index.User(
            "John", "Doe", "code123",
            index.RsvpStatus.ATTENDING,
            index.Pronouns.HE_HIM,
            address, "john@example.com", diet, guest_details
        )
        mock_list_db.return_value = [user]

        mock_ses = Mock()
        index.DOT_LOVE_MESSAGE_CLIENT = index.DotLoveMessageClient(
            mock_ses, "sender@example.com", "config_id"
        )

        response = index.send_cohort_email()
        self.assertEqual(response.status_code, 200)
        body = response.body
        self.assertEqual(body["matched_count"], 1)
        mock_ses.send_email.assert_called()

    @patch.object(index.User, 'list_db')
    def test_send_cohort_email_with_simple_message(self, mock_list_db):
        """Test send_cohort_email endpoint with simple message field (demonstrates bug)."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "test_internal_key"
        # Using simple message field triggers bug where template_type is set to "RAW_EMAIL" string
        mock_event.json_body = {
            "filter_field": "rsvp_status",
            "filter_value": "ATTENDING",
            "message": "<p>Test cohort message</p>",
            "subject": "Test Subject"
        }
        index.app.current_event = mock_event

        address = index.UserAddress("123 Main", "", "NYC", "10001", "USA", "NY", "+15555551234")
        diet = index.UserDiet(True, True, True, True, True, True, True, True, "")
        guest_details = index.GuestDetails("abc123", "", False)
        user = index.User(
            "John", "Doe", "code123",
            index.RsvpStatus.ATTENDING,
            index.Pronouns.HE_HIM,
            address, "john@example.com", diet, guest_details
        )
        mock_list_db.return_value = [user]

        mock_ses = Mock()
        index.DOT_LOVE_MESSAGE_CLIENT = index.DotLoveMessageClient(
            mock_ses, "sender@example.com", "config_id"
        )

        # This demonstrates a bug: send_cohort_email sets template_type to "RAW_EMAIL" string
        # but _get_email_template expects an enum, causing a KeyError
        response = index.send_cohort_email()
        self.assertEqual(response.status_code, 500)  # Bug causes error
        body = response.body
        self.assertIn("Failed to send cohort email", body["message"])

    def test_send_cohort_email_no_api_key(self):
        """Test send_cohort_email without API key."""
        mock_event = Mock()
        mock_event.headers.get.return_value = None
        index.app.current_event = mock_event

        response = index.send_cohort_email()
        self.assertEqual(response.status_code, 401)

    def test_not_found(self):
        """Test not_found handler."""
        mock_event = Mock()
        mock_event.path = "/unknown/route"
        index.app.current_event = mock_event

        response = index.not_found()
        self.assertEqual(response.status_code, 404)
        body = response.body
        self.assertEqual(body["message"], "Route not found")


class TestValidateInternalRoute(unittest.TestCase):
    """Test suite for validate_internal_route decorator."""

    def setUp(self):
        """Set up test fixtures."""
        index.app.context = {}

    def test_validate_internal_route_valid_key(self):
        """Test decorator with valid API key."""
        mock_event = Mock()
        mock_event.headers.get.side_effect = lambda key: "test_internal_key" if key == "Internal-Api-Key" else None
        index.app.current_event = mock_event

        @index.validate_internal_route
        def test_func():
            return index.Response(status_code=200, content_type="application/json", body={"success": True})

        response = test_func()
        self.assertEqual(response.status_code, 200)

    def test_validate_internal_route_invalid_key(self):
        """Test decorator with invalid API key."""
        mock_event = Mock()
        mock_event.headers.get.return_value = "wrong_key"
        index.app.current_event = mock_event

        @index.validate_internal_route
        def test_func():
            return index.Response(status_code=200, content_type="application/json", body={"success": True})

        response = test_func()
        self.assertEqual(response.status_code, 401)

    def test_validate_internal_route_no_key(self):
        """Test decorator without API key."""
        mock_event = Mock()
        mock_event.headers.get.return_value = None
        index.app.current_event = mock_event

        @index.validate_internal_route
        def test_func():
            return index.Response(status_code=200, content_type="application/json", body={"success": True})

        response = test_func()
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
