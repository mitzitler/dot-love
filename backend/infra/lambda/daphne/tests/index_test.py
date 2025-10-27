import json
import os
import sys
import unittest
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

# Set required environment variables before importing index
os.environ["user_table_name"] = "test_user_table"
os.environ["api_base_url"] = "https://test.api.com"
os.environ["internal_api_key"] = "test_key"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Add parent directory to path to import the lambda function
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock boto3 before importing index to avoid AWS credentials requirement
with patch("boto3.client"):
    import index


class TestHelperFunctions(unittest.TestCase):
    """Test suite for helper functions."""

    def test_deserialize_user(self):
        """Test deserialize_user with valid data."""
        item_data = {
            "first_last": {"S": "john_doe"},
            "first": {"S": "John"},
            "last": {"S": "Doe"},
            "high_score": {"N": "100"},
        }
        result = index.deserialize_user(item_data)
        self.assertEqual(result["first_last"], "john_doe")
        self.assertEqual(result["first"], "John")
        self.assertEqual(result["last"], "Doe")
        self.assertEqual(result["high_score"], Decimal("100"))

    def test_deserialize_user_empty(self):
        """Test deserialize_user with empty data."""
        result = index.deserialize_user(None)
        self.assertIsNone(result)

    def test_get_user_scores_list(self):
        """Test get_user_scores_list extracts scores correctly."""
        all_users = [
            {
                "first_last": {"S": "john_doe"},
                "first": {"S": "John"},
                "last": {"S": "Doe"},
                "high_score": {"N": "100"},
            },
            {
                "first_last": {"S": "jane_smith"},
                "first": {"S": "Jane"},
                "last": {"S": "Smith"},
                "high_score": {"N": "200"},
            },
            {
                "first_last": {"S": "bob_jones"},
                "first": {"S": "Bob"},
                "last": {"S": "Jones"},
                # No high_score - should be excluded
            },
        ]
        result = index.get_user_scores_list(all_users)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["first_last"], "john_doe")
        self.assertEqual(result[0]["score"], 100)
        self.assertEqual(result[1]["first_last"], "jane_smith")
        self.assertEqual(result[1]["score"], 200)

    def test_build_rankings_map(self):
        """Test build_rankings_map creates correct rankings."""
        user_scores = [
            {"first_last": "jane_smith", "first": "Jane", "last": "Smith", "score": 200},
            {"first_last": "john_doe", "first": "John", "last": "Doe", "score": 100},
            {"first_last": "bob_jones", "first": "Bob", "last": "Jones", "score": 50},
        ]
        rankings = index.build_rankings_map(user_scores, top_n=3)

        self.assertEqual(len(rankings), 3)
        self.assertEqual(rankings["jane_smith"]["position"], 1)
        self.assertEqual(rankings["jane_smith"]["score"], 200)
        self.assertEqual(rankings["john_doe"]["position"], 2)
        self.assertEqual(rankings["bob_jones"]["position"], 3)

    def test_build_rankings_map_top_n(self):
        """Test build_rankings_map respects top_n parameter."""
        user_scores = [
            {"first_last": f"user_{i}", "first": "User", "last": str(i), "score": 100 - i}
            for i in range(10)
        ]
        rankings = index.build_rankings_map(user_scores, top_n=5)

        self.assertEqual(len(rankings), 5)
        self.assertIn("user_0", rankings)
        self.assertIn("user_4", rankings)
        self.assertNotIn("user_5", rankings)

    def test_update_user_score_in_list_existing_user(self):
        """Test updating an existing user's score."""
        user_scores = [
            {"first_last": "john_doe", "first": "John", "last": "Doe", "score": 100},
            {"first_last": "jane_smith", "first": "Jane", "last": "Smith", "score": 200},
        ]
        result = index.update_user_score_in_list(
            user_scores, "john_doe", 150, "John", "Doe"
        )

        self.assertEqual(len(result), 2)
        john_entry = next(u for u in result if u["first_last"] == "john_doe")
        self.assertEqual(john_entry["score"], 150)

    def test_update_user_score_in_list_new_user(self):
        """Test adding a new user to the scores list."""
        user_scores = [
            {"first_last": "john_doe", "first": "John", "last": "Doe", "score": 100},
        ]
        result = index.update_user_score_in_list(
            user_scores, "jane_smith", 200, "Jane", "Smith"
        )

        self.assertEqual(len(result), 2)
        jane_entry = next(u for u in result if u["first_last"] == "jane_smith")
        self.assertEqual(jane_entry["score"], 200)

    def test_get_bump_notification_message_dethroned(self):
        """Test notification message for being dethroned from #1."""
        message = index.get_bump_notification_message(1, 2, "Jane", "Smith", 300)
        self.assertIn("throne", message.lower())
        self.assertIn("Jane Smith", message)
        self.assertIn("#1", message)
        self.assertIn("#2", message)

    def test_get_bump_notification_message_out_of_top_5(self):
        """Test notification message for being bumped out of top 5."""
        message = index.get_bump_notification_message(5, 6, "Jane", "Smith", 300)
        self.assertIn("top 5", message)
        self.assertIn("Jane Smith", message)
        self.assertIn("#6", message)

    def test_get_bump_notification_message_generic(self):
        """Test generic bump down notification message."""
        message = index.get_bump_notification_message(3, 4, "Jane", "Smith", 300)
        self.assertIn("Jane Smith", message)
        self.assertIn("#3", message)
        self.assertIn("#4", message)
        self.assertIn("300", message)


class TestAPIEndpoints(unittest.TestCase):
    """Test suite for API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        # Set environment variables
        os.environ["user_table_name"] = "test_user_table"
        os.environ["api_base_url"] = "https://test.api.com"
        os.environ["internal_api_key"] = "test_key"

        # Mock the CWDynamoClient
        self.mock_dynamo_client = Mock()
        index.CW_DYNAMO_CLIENT = self.mock_dynamo_client

        # Mock app context
        index.app.context = {"trace_id": "test_trace_123"}

    @patch("index.requests.post")
    def test_send_text_notification_success(self, mock_post):
        """Test successful text notification."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = index.send_text_notification("john_doe", "Test message")

        self.assertTrue(result)
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]["json"]["first_last"], "john_doe")
        self.assertEqual(
            call_args[1]["json"]["template_details"]["raw_text"], "Test message"
        )

    @patch("index.requests.post")
    def test_send_text_notification_failure(self, mock_post):
        """Test failed text notification."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_post.return_value = mock_response

        result = index.send_text_notification("john_doe", "Test message")

        self.assertFalse(result)

    def test_get_scoreboard_success(self):
        """Test get_scoreboard endpoint returns top 5 scores."""
        # Mock DynamoDB response
        self.mock_dynamo_client.get_all.return_value = [
            {
                "first_last": {"S": "user1"},
                "first": {"S": "User"},
                "last": {"S": "One"},
                "high_score": {"N": "500"},
            },
            {
                "first_last": {"S": "user2"},
                "first": {"S": "User"},
                "last": {"S": "Two"},
                "high_score": {"N": "400"},
            },
            {
                "first_last": {"S": "user3"},
                "first": {"S": "User"},
                "last": {"S": "Three"},
                "high_score": {"N": "300"},
            },
            {
                "first_last": {"S": "user4"},
                "first": {"S": "User"},
                "last": {"S": "Four"},
                "high_score": {"N": "200"},
            },
            {
                "first_last": {"S": "user5"},
                "first": {"S": "User"},
                "last": {"S": "Five"},
                "high_score": {"N": "100"},
            },
            {
                "first_last": {"S": "user6"},
                "first": {"S": "User"},
                "last": {"S": "Six"},
                "high_score": {"N": "50"},
            },
        ]

        response = index.get_scoreboard()

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.body)
        self.assertEqual(len(body), 5)
        self.assertEqual(body[0]["score"], 500)
        self.assertEqual(body[0]["userName"], "User One")
        self.assertEqual(body[4]["score"], 100)

    def test_get_scoreboard_excludes_zero_scores(self):
        """Test get_scoreboard excludes users with score of 0."""
        self.mock_dynamo_client.get_all.return_value = [
            {
                "first_last": {"S": "user1"},
                "first": {"S": "User"},
                "last": {"S": "One"},
                "high_score": {"N": "100"},
            },
            {
                "first_last": {"S": "user2"},
                "first": {"S": "User"},
                "last": {"S": "Two"},
                "high_score": {"N": "0"},
            },
        ]

        response = index.get_scoreboard()

        body = json.loads(response.body)
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["userName"], "User One")

    @patch("index.send_text_notification")
    def test_submit_score_new_high_score(self, mock_send_text):
        """Test submitting a new high score."""
        # Mock current event
        mock_event = Mock()
        mock_event.json_body = {"score": 150, "first": "John", "last": "Doe"}
        index.app.current_event = mock_event

        # Mock get user
        self.mock_dynamo_client.get.return_value = {
            "first_last": {"S": "john_doe"},
            "first": {"S": "John"},
            "last": {"S": "Doe"},
            "high_score": {"N": "100"},
        }

        # Mock get_all for rankings
        self.mock_dynamo_client.get_all.return_value = [
            {
                "first_last": {"S": "john_doe"},
                "first": {"S": "John"},
                "last": {"S": "Doe"},
                "high_score": {"N": "100"},
            },
        ]

        response = index.submit_score()

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.body)
        self.assertTrue(body["isHighScore"])
        self.assertEqual(body["score"], 150)
        self.assertEqual(body["previousHighScore"], 100)

        # Verify database update was called
        self.mock_dynamo_client.update.assert_called_once()

        # Verify notification was sent
        mock_send_text.assert_called()

    def test_submit_score_not_high_score(self):
        """Test submitting a score that's not a high score."""
        mock_event = Mock()
        mock_event.json_body = {"score": 50, "first": "John", "last": "Doe"}
        index.app.current_event = mock_event

        self.mock_dynamo_client.get.return_value = {
            "first_last": {"S": "john_doe"},
            "first": {"S": "John"},
            "last": {"S": "Doe"},
            "high_score": {"N": "100"},
        }

        response = index.submit_score()

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.body)
        self.assertFalse(body["isHighScore"])
        self.assertEqual(body["score"], 50)
        self.assertEqual(body["currentHighScore"], 100)

        # Verify database was not updated
        self.mock_dynamo_client.update.assert_not_called()

    def test_submit_score_user_not_found(self):
        """Test submitting a score for non-existent user."""
        mock_event = Mock()
        mock_event.json_body = {"score": 100, "first": "John", "last": "Doe"}
        index.app.current_event = mock_event

        self.mock_dynamo_client.get.return_value = None

        response = index.submit_score()

        self.assertEqual(response.status_code, 404)
        body = json.loads(response.body)
        self.assertIn("error", body)

    def test_submit_score_missing_fields(self):
        """Test submitting a score with missing required fields."""
        mock_event = Mock()
        mock_event.json_body = {"score": 100}  # Missing first and last
        index.app.current_event = mock_event

        response = index.submit_score()

        self.assertEqual(response.status_code, 400)
        body = json.loads(response.body)
        self.assertIn("error", body)

    @patch("index.send_text_notification")
    def test_notify_bumped_users(self, mock_send_text):
        """Test notify_bumped_users sends notifications correctly."""
        old_rankings = {
            "user1": {"position": 1, "first": "User", "last": "One", "score": 400},
            "user2": {"position": 2, "first": "User", "last": "Two", "score": 300},
        }

        new_rankings = {
            "user3": {"position": 1, "first": "User", "last": "Three", "score": 500},
            "user1": {"position": 2, "first": "User", "last": "One", "score": 400},
            "user2": {"position": 3, "first": "User", "last": "Two", "score": 300},
        }

        index.notify_bumped_users(
            old_rankings, new_rankings, "user3", "User", "Three", 500
        )

        # Should send 2 notifications (user1 and user2 were bumped)
        self.assertEqual(mock_send_text.call_count, 2)

        # Check user1 got the dethroned message
        calls = mock_send_text.call_args_list
        user1_call = next(c for c in calls if c[0][0] == "user1")
        self.assertIn("throne", user1_call[0][1].lower())


class TestNotifyBumpedUsersIntegration(unittest.TestCase):
    """Integration tests for the notify_bumped_users function."""

    @patch("index.send_text_notification")
    def test_user_bumped_out_of_top_5(self, mock_send_text):
        """Test notification when user is bumped from #5 to #6."""
        old_rankings = {
            "user5": {"position": 5, "first": "User", "last": "Five", "score": 100},
        }

        new_rankings = {
            "scorer": {"position": 5, "first": "New", "last": "Scorer", "score": 150},
            "user5": {"position": 6, "first": "User", "last": "Five", "score": 100},
        }

        index.notify_bumped_users(
            old_rankings, new_rankings, "scorer", "New", "Scorer", 150
        )

        mock_send_text.assert_called_once()
        call_args = mock_send_text.call_args[0]
        self.assertEqual(call_args[0], "user5")
        self.assertIn("top 5", call_args[1])


if __name__ == "__main__":
    unittest.main()
