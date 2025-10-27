import json
import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

# Set required environment variables before importing index
os.environ["ses_s3_bucket_name"] = "test-ses-bucket"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Add parent directory to path to import the lambda function
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock boto3 before importing index to avoid AWS credentials requirement
with patch("boto3.client"):
    import index


class TestSESHandler(unittest.TestCase):
    """Test suite for SES Lambda handler function."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock S3 client
        self.mock_s3_client = Mock()
        index.S3_CLIENT = self.mock_s3_client

    def test_handler_success(self):
        """Test handler successfully processes SNS event and stores in S3."""
        # Create a mock SNS event
        test_message = "Test email notification message"
        test_message_id = "test-message-id-12345"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()

        # Call handler
        result = index.handler(event, context)

        # Verify S3 put_object was called with correct parameters
        self.mock_s3_client.put_object.assert_called_once_with(
            Bucket="test-ses-bucket",
            Key=test_message_id,
            Body=test_message
        )

        # Verify return value
        self.assertEqual(result, test_message)

    def test_handler_with_json_message(self):
        """Test handler with JSON-formatted SNS message."""
        test_message = json.dumps({
            "notificationType": "Bounce",
            "bounce": {
                "bounceType": "Permanent",
                "bouncedRecipients": [
                    {"emailAddress": "test@example.com"}
                ]
            }
        })
        test_message_id = "json-message-id"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()

        result = index.handler(event, context)

        # Verify S3 storage
        self.mock_s3_client.put_object.assert_called_once()
        call_args = self.mock_s3_client.put_object.call_args
        self.assertEqual(call_args[1]["Bucket"], "test-ses-bucket")
        self.assertEqual(call_args[1]["Key"], test_message_id)
        self.assertEqual(call_args[1]["Body"], test_message)

        # Verify return value
        self.assertEqual(result, test_message)

    def test_handler_with_multiline_message(self):
        """Test handler with multiline message content."""
        test_message = """Line 1: This is a test
Line 2: Multiple lines
Line 3: Should be preserved"""
        test_message_id = "multiline-message-id"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()

        result = index.handler(event, context)

        # Verify message is stored correctly
        self.mock_s3_client.put_object.assert_called_once_with(
            Bucket="test-ses-bucket",
            Key=test_message_id,
            Body=test_message
        )

        self.assertEqual(result, test_message)

    def test_handler_with_empty_message(self):
        """Test handler with empty message content."""
        test_message = ""
        test_message_id = "empty-message-id"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()

        result = index.handler(event, context)

        # Should still store empty message
        self.mock_s3_client.put_object.assert_called_once_with(
            Bucket="test-ses-bucket",
            Key=test_message_id,
            Body=""
        )

        self.assertEqual(result, "")

    def test_handler_with_special_characters(self):
        """Test handler with special characters in message."""
        test_message = "Special chars: <>&\"'@#$%^&*()\n\t\r"
        test_message_id = "special-chars-id"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()

        result = index.handler(event, context)

        # Verify special characters are preserved
        self.mock_s3_client.put_object.assert_called_once_with(
            Bucket="test-ses-bucket",
            Key=test_message_id,
            Body=test_message
        )

        self.assertEqual(result, test_message)

    def test_handler_with_unicode_characters(self):
        """Test handler with unicode characters in message."""
        test_message = "Unicode: 你好 🎉 émojis café"
        test_message_id = "unicode-message-id"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()

        result = index.handler(event, context)

        # Verify unicode is preserved
        self.mock_s3_client.put_object.assert_called_once_with(
            Bucket="test-ses-bucket",
            Key=test_message_id,
            Body=test_message
        )

        self.assertEqual(result, test_message)

    def test_handler_with_long_message(self):
        """Test handler with a very long message."""
        # Create a long message (10KB)
        test_message = "A" * 10000
        test_message_id = "long-message-id"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()

        result = index.handler(event, context)

        # Verify long message is stored correctly
        self.mock_s3_client.put_object.assert_called_once()
        call_args = self.mock_s3_client.put_object.call_args
        self.assertEqual(call_args[1]["Key"], test_message_id)
        self.assertEqual(len(call_args[1]["Body"]), 10000)

        self.assertEqual(result, test_message)

    def test_handler_s3_error(self):
        """Test handler when S3 put_object fails."""
        test_message = "Test message"
        test_message_id = "error-message-id"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()

        # Mock S3 to raise an exception
        self.mock_s3_client.put_object.side_effect = Exception("S3 Error")

        # Handler should raise the exception
        with self.assertRaises(Exception) as cm:
            index.handler(event, context)

        self.assertEqual(str(cm.exception), "S3 Error")

    def test_handler_uses_correct_bucket(self):
        """Test handler uses the correct S3 bucket from environment variable."""
        # Change the bucket name
        os.environ["ses_s3_bucket_name"] = "different-bucket"

        test_message = "Test message"
        test_message_id = "test-id"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()

        # Note: The bucket name is loaded at module import time,
        # so it will still use the original "test-ses-bucket"
        result = index.handler(event, context)

        # Verify it used the bucket name from the initial environment
        call_args = self.mock_s3_client.put_object.call_args
        self.assertEqual(call_args[1]["Bucket"], "test-ses-bucket")

        # Reset environment
        os.environ["ses_s3_bucket_name"] = "test-ses-bucket"

    def test_handler_uses_message_id_as_key(self):
        """Test handler uses MessageId as the S3 object key."""
        test_message = "Test message"
        test_message_id = "unique-message-id-abc-123"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()

        result = index.handler(event, context)

        # Verify the MessageId is used as the S3 key
        call_args = self.mock_s3_client.put_object.call_args
        self.assertEqual(call_args[1]["Key"], test_message_id)


class TestSESHandlerEventStructure(unittest.TestCase):
    """Test suite for different SNS event structures."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_s3_client = Mock()
        index.S3_CLIENT = self.mock_s3_client

    def test_handler_with_multiple_records(self):
        """Test handler only processes the first record."""
        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": "First message",
                        "MessageId": "first-id"
                    }
                },
                {
                    "Sns": {
                        "Message": "Second message",
                        "MessageId": "second-id"
                    }
                }
            ]
        }

        context = Mock()

        result = index.handler(event, context)

        # Should only process first record
        self.mock_s3_client.put_object.assert_called_once_with(
            Bucket="test-ses-bucket",
            Key="first-id",
            Body="First message"
        )

        self.assertEqual(result, "First message")

    def test_handler_with_full_sns_event(self):
        """Test handler with complete SNS event structure."""
        event = {
            "Records": [
                {
                    "EventSource": "aws:sns",
                    "EventVersion": "1.0",
                    "EventSubscriptionArn": "arn:aws:sns:us-east-1:123456789012:test-topic",
                    "Sns": {
                        "Type": "Notification",
                        "MessageId": "full-event-id",
                        "TopicArn": "arn:aws:sns:us-east-1:123456789012:test-topic",
                        "Subject": "Test Subject",
                        "Message": "Full SNS event message",
                        "Timestamp": "2025-01-01T00:00:00.000Z",
                        "SignatureVersion": "1",
                        "Signature": "test-signature",
                        "SigningCertUrl": "https://test.com/cert",
                        "UnsubscribeUrl": "https://test.com/unsubscribe"
                    }
                }
            ]
        }

        context = Mock()

        result = index.handler(event, context)

        # Should extract and store the message correctly
        self.mock_s3_client.put_object.assert_called_once_with(
            Bucket="test-ses-bucket",
            Key="full-event-id",
            Body="Full SNS event message"
        )

        self.assertEqual(result, "Full SNS event message")


class TestModuleImport(unittest.TestCase):
    """Test suite for module-level imports and configuration."""

    def test_environment_variable_loaded(self):
        """Test that SES_S3_BUCKET_NAME is loaded from environment."""
        # The module should have loaded the bucket name
        self.assertEqual(index.SES_S3_BUCKET_NAME, "test-ses-bucket")

    def test_s3_client_created(self):
        """Test that S3_CLIENT is initialized (mocked in tests)."""
        self.assertIsNotNone(index.S3_CLIENT)


class TestSESIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for common SES use cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_s3_client = Mock()
        index.S3_CLIENT = self.mock_s3_client

    def test_bounce_notification(self):
        """Test processing a bounce notification from SES."""
        bounce_notification = {
            "notificationType": "Bounce",
            "bounce": {
                "bounceType": "Permanent",
                "bounceSubType": "General",
                "bouncedRecipients": [
                    {
                        "emailAddress": "bounce@example.com",
                        "action": "failed",
                        "status": "5.1.1",
                        "diagnosticCode": "smtp; 550 5.1.1 user unknown"
                    }
                ],
                "timestamp": "2025-01-01T12:00:00.000Z",
                "feedbackId": "feedback-id-123"
            },
            "mail": {
                "timestamp": "2025-01-01T12:00:00.000Z",
                "source": "sender@example.com",
                "messageId": "mail-message-id",
                "destination": ["bounce@example.com"]
            }
        }

        test_message = json.dumps(bounce_notification)
        test_message_id = "bounce-notification-id"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()
        result = index.handler(event, context)

        # Verify the bounce notification is stored
        self.mock_s3_client.put_object.assert_called_once()
        call_args = self.mock_s3_client.put_object.call_args
        self.assertEqual(call_args[1]["Key"], test_message_id)

        # Verify the stored message can be parsed back
        stored_message = call_args[1]["Body"]
        parsed = json.loads(stored_message)
        self.assertEqual(parsed["notificationType"], "Bounce")
        self.assertEqual(parsed["bounce"]["bounceType"], "Permanent")

    def test_complaint_notification(self):
        """Test processing a complaint notification from SES."""
        complaint_notification = {
            "notificationType": "Complaint",
            "complaint": {
                "complainedRecipients": [
                    {"emailAddress": "complaint@example.com"}
                ],
                "timestamp": "2025-01-01T12:00:00.000Z",
                "feedbackId": "feedback-id-456",
                "complaintFeedbackType": "abuse"
            },
            "mail": {
                "timestamp": "2025-01-01T12:00:00.000Z",
                "source": "sender@example.com",
                "messageId": "mail-message-id",
                "destination": ["complaint@example.com"]
            }
        }

        test_message = json.dumps(complaint_notification)
        test_message_id = "complaint-notification-id"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()
        result = index.handler(event, context)

        # Verify the complaint notification is stored
        self.mock_s3_client.put_object.assert_called_once()
        call_args = self.mock_s3_client.put_object.call_args

        stored_message = call_args[1]["Body"]
        parsed = json.loads(stored_message)
        self.assertEqual(parsed["notificationType"], "Complaint")
        self.assertEqual(parsed["complaint"]["complaintFeedbackType"], "abuse")

    def test_delivery_notification(self):
        """Test processing a delivery notification from SES."""
        delivery_notification = {
            "notificationType": "Delivery",
            "delivery": {
                "timestamp": "2025-01-01T12:00:00.000Z",
                "processingTimeMillis": 1234,
                "recipients": ["success@example.com"],
                "smtpResponse": "250 2.0.0 OK",
                "reportingMTA": "example.com"
            },
            "mail": {
                "timestamp": "2025-01-01T12:00:00.000Z",
                "source": "sender@example.com",
                "messageId": "mail-message-id",
                "destination": ["success@example.com"]
            }
        }

        test_message = json.dumps(delivery_notification)
        test_message_id = "delivery-notification-id"

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": test_message,
                        "MessageId": test_message_id
                    }
                }
            ]
        }

        context = Mock()
        result = index.handler(event, context)

        # Verify the delivery notification is stored
        self.mock_s3_client.put_object.assert_called_once()
        call_args = self.mock_s3_client.put_object.call_args

        stored_message = call_args[1]["Body"]
        parsed = json.loads(stored_message)
        self.assertEqual(parsed["notificationType"], "Delivery")
        self.assertEqual(parsed["delivery"]["smtpResponse"], "250 2.0.0 OK")


if __name__ == "__main__":
    unittest.main()
