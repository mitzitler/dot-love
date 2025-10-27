import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from moto import mock_aws
import boto3

# Set required environment variables before importing
os.environ["user_table_name"] = "test-users-table"
os.environ["api_base_url"] = "https://api.test.com"
os.environ["internal_api_key"] = "test-key"

from index import (
    app,
    get_user_scores_list,
    deserialize_user,
    GAME_NAMES
)


@pytest.fixture
def sample_users():
    """Sample DynamoDB user data."""
    return [
        {
            "first_last": {"S": "john_doe"},
            "high_score_militsa": {"N": "150"},
            "high_score_pritham": {"N": "200"}
        },
        {
            "first_last": {"S": "jane_smith"},
            "high_score_militsa": {"N": "300"},
            "high_score_pritham": {"N": "100"}
        },
        {
            "first_last": {"S": "bob_jones"},
            "high_score_militsa": {"N": "225"}
        }
    ]


class TestGetUserScoresList:
    """Test the get_user_scores_list helper function."""

    def test_get_militsa_scores(self, sample_users):
        """Test extracting militsa game scores."""
        scores = get_user_scores_list(sample_users, "militsa")
        
        assert len(scores) == 3
        assert scores[0]["first"] == "John"
        assert scores[0]["last"] == "Doe"
        assert scores[0]["score"] == 150
        
        assert scores[1]["first"] == "Jane"
        assert scores[1]["last"] == "Smith"
        assert scores[1]["score"] == 300

    def test_get_pritham_scores(self, sample_users):
        """Test extracting pritham game scores."""
        scores = get_user_scores_list(sample_users, "pritham")
        
        assert len(scores) == 2  # Only 2 users have pritham scores
        assert scores[0]["score"] == 200
        assert scores[1]["score"] == 100

    def test_scores_sorted_descending(self, sample_users):
        """Test that scores are sorted in descending order."""
        scores = get_user_scores_list(sample_users, "militsa")
        
        assert scores[0]["score"] == 300  # jane_smith
        assert scores[1]["score"] == 225  # bob_jones
        assert scores[2]["score"] == 150  # john_doe

    def test_name_extraction_from_composite_key(self, sample_users):
        """Test that first/last names are properly extracted from first_last key."""
        scores = get_user_scores_list(sample_users, "militsa")
        
        for score in scores:
            assert "first" in score
            assert "last" in score
            assert score["first"].istitle()  # First letter capitalized
            assert score["last"].istitle()

    def test_handles_missing_scores(self):
        """Test handling users without game scores."""
        users = [
            {"first_last": {"S": "test_user"}},  # No scores
        ]
        
        scores = get_user_scores_list(users, "militsa")
        assert len(scores) == 0


class TestDeserializeUser:
    """Test the deserialize_user helper function."""

    def test_deserialize_basic_user(self):
        """Test deserializing basic user data."""
        raw_user = {
            "first_last": {"S": "john_doe"},
            "high_score_militsa": {"N": "150"}
        }
        
        user = deserialize_user(raw_user)
        assert user["first_last"] == "john_doe"
        assert user["high_score_militsa"] == 150

    def test_deserialize_none(self):
        """Test deserializing None returns None."""
        assert deserialize_user(None) is None

    def test_deserialize_empty_dict(self):
        """Test deserializing empty dict."""
        result = deserialize_user({})
        assert result == {}


@mock_aws
class TestGetScoreboardEndpoint:
    """Test the GET /scoreboard endpoint."""

    @pytest.fixture(autouse=True)
    def setup_dynamodb(self):
        """Set up DynamoDB table for testing."""
        dynamodb = boto3.client("dynamodb", region_name="us-east-1")
        
        # Create table
        dynamodb.create_table(
            TableName="test-users-table",
            KeySchema=[{"AttributeName": "first_last", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "first_last", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        
        # Add test data
        dynamodb.put_item(
            TableName="test-users-table",
            Item={
                "first_last": {"S": "alice_wonder"},
                "high_score_militsa": {"N": "500"},
                "high_score_pritham": {"N": "350"}
            }
        )
        dynamodb.put_item(
            TableName="test-users-table",
            Item={
                "first_last": {"S": "bob_builder"},
                "high_score_militsa": {"N": "400"}
            }
        )

    def test_get_scoreboard_militsa(self):
        """Test getting militsa scoreboard."""
        event = {
            "requestContext": {"http": {"method": "GET"}},
            "rawPath": "/daphne/scoreboard",
            "queryStringParameters": {"game": "militsa"},
            "headers": {}
        }
        
        response = app.resolve(event, {})
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert len(body) > 0
        assert body[0]["score"] == 500  # alice_wonder has highest score

    def test_get_scoreboard_pritham(self):
        """Test getting pritham scoreboard."""
        event = {
            "requestContext": {"http": {"method": "GET"}},
            "rawPath": "/daphne/scoreboard",
            "queryStringParameters": {"game": "pritham"},
            "headers": {}
        }
        
        response = app.resolve(event, {})
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert len(body) == 1  # Only alice has pritham score
        assert body[0]["score"] == 350

    def test_get_scoreboard_invalid_game(self):
        """Test getting scoreboard with invalid game name."""
        event = {
            "requestContext": {"http": {"method": "GET"}},
            "rawPath": "/daphne/scoreboard",
            "queryStringParameters": {"game": "invalid_game"},
            "headers": {}
        }
        
        response = app.resolve(event, {})
        
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "Invalid game" in body["message"]

    def test_get_scoreboard_missing_game_param(self):
        """Test getting scoreboard without game parameter."""
        event = {
            "requestContext": {"http": {"method": "GET"}},
            "rawPath": "/daphne/scoreboard",
            "queryStringParameters": {},
            "headers": {}
        }
        
        response = app.resolve(event, {})
        
        assert response["statusCode"] == 400


@mock_aws
class TestSubmitScoreEndpoint:
    """Test the POST /score endpoint."""

    @pytest.fixture(autouse=True)
    def setup_dynamodb(self):
        """Set up DynamoDB table for testing."""
        dynamodb = boto3.client("dynamodb", region_name="us-east-1")
        
        # Create table
        dynamodb.create_table(
            TableName="test-users-table",
            KeySchema=[{"AttributeName": "first_last", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "first_last", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        
        # Add test user
        dynamodb.put_item(
            TableName="test-users-table",
            Item={
                "first_last": {"S": "test_user"},
                "high_score_militsa": {"N": "100"}
            }
        )

    @patch("index.send_text_notification")
    def test_submit_new_high_score(self, mock_send_text):
        """Test submitting a new high score."""
        mock_send_text.return_value = True
        
        event = {
            "requestContext": {"http": {"method": "POST"}},
            "rawPath": "/daphne/score",
            "headers": {"X-First-Last": "test_user"},
            "body": json.dumps({
                "score": 250,
                "first": "Test",
                "last": "User",
                "game": "militsa"
            })
        }
        
        response = app.resolve(event, {})
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["isHighScore"] is True
        assert body["message"] == "New high score!"
        
        # Verify notification was sent
        mock_send_text.assert_called_once()

    @patch("index.send_text_notification")
    def test_submit_not_high_score(self, mock_send_text):
        """Test submitting a score that's not a high score."""
        event = {
            "requestContext": {"http": {"method": "POST"}},
            "rawPath": "/daphne/score",
            "headers": {"X-First-Last": "test_user"},
            "body": json.dumps({
                "score": 50,  # Lower than existing 100
                "first": "Test",
                "last": "User",
                "game": "militsa"
            })
        }
        
        response = app.resolve(event, {})
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["isHighScore"] is False
        
        # Verify notification was NOT sent
        mock_send_text.assert_not_called()

    def test_submit_score_invalid_game(self):
        """Test submitting score with invalid game name."""
        event = {
            "requestContext": {"http": {"method": "POST"}},
            "rawPath": "/daphne/score",
            "headers": {"X-First-Last": "test_user"},
            "body": json.dumps({
                "score": 200,
                "first": "Test",
                "last": "User",
                "game": "invalid_game"
            })
        }
        
        response = app.resolve(event, {})
        
        assert response["statusCode"] == 400

    @patch("index.send_text_notification")
    def test_submit_first_score_for_game(self, mock_send_text):
        """Test submitting first score for a game (no existing high score)."""
        mock_send_text.return_value = True
        
        event = {
            "requestContext": {"http": {"method": "POST"}},
            "rawPath": "/daphne/score",
            "headers": {"X-First-Last": "test_user"},
            "body": json.dumps({
                "score": 150,
                "first": "Test",
                "last": "User",
                "game": "pritham"  # No existing pritham score
            })
        }
        
        response = app.resolve(event, {})
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["isHighScore"] is True
        
        # Verify notification was sent
        mock_send_text.assert_called_once()


class TestGameNamesConstant:
    """Test the GAME_NAMES constant."""

    def test_game_names_defined(self):
        """Test that game names are properly defined."""
        assert "militsa" in GAME_NAMES
        assert "pritham" in GAME_NAMES
        assert GAME_NAMES["militsa"] == "Don't Drop Militsa"
        assert GAME_NAMES["pritham"] == "Stop Pritham"
