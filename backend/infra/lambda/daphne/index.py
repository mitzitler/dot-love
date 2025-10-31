import json
import os
import uuid
from datetime import datetime
from boto3.dynamodb.types import TypeDeserializer

import boto3
import requests
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.event_handler.api_gateway import (
    APIGatewayHttpResolver,
    ProxyEventType,
)
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator

# Environment Variables
USER_TABLE_NAME = os.environ["user_table_name"]
SCOREBOARD_TABLE_NAME = os.environ["scoreboard_table_name"]
API_BASE_URL = os.environ.get("api_base_url", "https://api.mitzimatthew.love")
INTERNAL_API_KEY = os.environ.get("internal_api_key", "")

# Game name mapping
GAME_NAMES = {
    "militsa": "Don't Drop Militsa",
    "pritham": "Stop Pritham",
    "jules": "JulesCraft"
}

# Powertools logger
log = Logger(service="daphne")

# Powertools routing
app = APIGatewayHttpResolver()


########################################################
# Helper Functions
########################################################
def deserialize_user(item_data):
    """Deserialize user data from DynamoDB."""
    if not item_data:
        return None

    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in item_data.items()}


def send_text_notification(first_last, message_text):
    """
    Send a text notification via Gizmo service.

    :param first_last: User ID in first_last format
    :param message_text: The text message to send
    :return: True if successful, False otherwise
    """
    try:
        gizmo_endpoint = f"{API_BASE_URL}/gizmo/text"
        payload = {
            "is_blast": False,
            "template_type": "RAW_TEXT",
            "template_details": {"raw": message_text},
            "recipient_phone": None,  # Will be looked up by Gizmo
            "trace": app.context.get("trace_id", "🤷"),
            "first_last": first_last,
        }

        headers = {
            "Content-Type": "application/json",
            "Internal-Api-Key": INTERNAL_API_KEY,
            "X-First-Last": first_last,
        }

        log.info(f"Sending text notification to {first_last}")
        response = requests.post(gizmo_endpoint, json=payload, headers=headers)

        if response.status_code != 200:
            log.error(f"Failed to send text notification: {response.text}")
            return False

        log.info(f"Successfully sent text notification to {first_last}")
        return True
    except Exception as e:
        log.exception(f"Error sending text notification: {str(e)}")
        return False


def get_user_scores_list(all_users, game):
    """
    Extract and return list of user scores from all users for a specific game.

    :param all_users: List of raw user data from DynamoDB
    :param game: Game identifier (e.g., "militsa" or "pritham")
    :return: List of dicts with first_last, first, last, score
    """
    score_field = f"high_score_{game}"
    user_scores = []
    for user_data_item in all_users:
        user_item = deserialize_user(user_data_item)
        if user_item and user_item.get(score_field) is not None:
            # Extract first and last from first_last key
            first_last = user_item.get("first_last", "_")
            parts = first_last.split("_")
            first = parts[0] if len(parts) > 0 else ""
            last = parts[1] if len(parts) > 1 else ""

            user_scores.append(
                {
                    "first_last": first_last,
                    "first": first,
                    "last": last,
                    "score": int(user_item.get(score_field, 0)),
                }
            )
    return user_scores


def build_rankings_map(user_scores, top_n=5):
    """
    Build a rankings map from user scores.

    :param user_scores: List of user score dicts (must be sorted)
    :param top_n: Number of top positions to include
    :return: Dict mapping first_last to rank info
    """
    rankings = {}
    for idx, user_score in enumerate(user_scores[:top_n], start=1):
        rankings[user_score["first_last"]] = {
            "position": idx,
            "first": user_score["first"],
            "last": user_score["last"],
            "score": user_score["score"],
        }
    return rankings


def update_user_score_in_list(user_scores, first_last, new_score, first, last):
    """
    Update or add user score in the scores list.

    :param user_scores: List of user score dicts
    :param first_last: User ID
    :param new_score: New score value
    :param first: User's first name
    :param last: User's last name
    :return: Updated user_scores list
    """
    updated = False
    for user_score in user_scores:
        if user_score["first_last"] == first_last:
            user_score["score"] = new_score
            updated = True
            break

    # If user wasn't in the list before, add them
    if not updated:
        user_scores.append(
            {
                "first_last": first_last,
                "first": first,
                "last": last,
                "score": new_score,
            }
        )
    return user_scores


def get_bump_notification_message(
    old_pos, new_pos, scorer_first, scorer_last, new_score, game_name
):
    """
    Generate notification message for users who got bumped down.

    :param old_pos: Old leaderboard position
    :param new_pos: New leaderboard position
    :param scorer_first: First name of person who scored
    :param scorer_last: Last name of person who scored
    :param new_score: The new score that caused the bump
    :param game_name: Friendly name of the game
    :return: Notification message string
    """
    scorer_name = f"{scorer_first.title()} {scorer_last.title()}"

    if old_pos == 1 and new_pos == 2:
        return f"👑💔 The throne has been usurped in {game_name}! {scorer_name} just scored {new_score} points and dethroned you from #1! You're now #2. Can you reclaim your crown? 🎮"
    elif old_pos == 5 and new_pos == 6:
        return f"😱 Oh no! {scorer_name} just scored {new_score} points in {game_name} and bumped you out of the top 5! You're now #6. Time for a comeback! 🎮"
    else:
        return f"📉 {scorer_name} just scored {new_score} points in {game_name} and bumped you from #{old_pos} to #{new_pos} on the leaderboard! Time to step up your game! 🎮"


def notify_bumped_users(
    old_rankings, new_rankings, scorer_first_last, scorer_first, scorer_last, new_score, game_name
):
    """
    Send notifications to users who got bumped down in rankings.

    :param old_rankings: Previous rankings map
    :param new_rankings: New rankings map
    :param scorer_first_last: User ID of person who just scored
    :param scorer_first: First name of person who scored
    :param scorer_last: Last name of person who scored
    :param new_score: The new score
    :param game_name: Friendly name of the game
    """
    for user_fl, new_rank_info in new_rankings.items():
        if user_fl == scorer_first_last:
            continue  # Skip the person who just scored

        old_rank_info = old_rankings.get(user_fl)
        if old_rank_info:
            old_pos = old_rank_info["position"]
            new_pos = new_rank_info["position"]

            if new_pos > old_pos:  # They got bumped down
                message = get_bump_notification_message(
                    old_pos, new_pos, scorer_first, scorer_last, new_score, game_name
                )
                send_text_notification(user_fl, message)


def write_score_to_scoreboard(game, score, first_last, first, last, date_str):
    """
    Write a score entry to the scoreboard table.

    :param game: Game name (e.g., "militsa")
    :param score: Score value
    :param first_last: User ID in format "first_last"
    :param first: User's first name
    :param last: User's last name
    :param date_str: Date string in YYYY-MM-DD format
    """
    # Create sort key: date#score#first_last with zero-padded 5-digit score
    # Format example: "2025-10-27#00450#jane_doe"
    # We invert the score (99999 - score) so higher scores come first lexicographically
    inverted_score = 99999 - score
    date_score_user = f"{date_str}#{inverted_score:05d}#{first_last}"

    item = {
        "game": {"S": game},
        "date_score_user": {"S": date_score_user},
        "score": {"N": str(score)},
        "first_last": {"S": first_last},
        "first": {"S": first},
        "last": {"S": last},
        "date": {"S": date_str},
        "timestamp": {"S": datetime.utcnow().isoformat()},
    }

    CW_DYNAMO_CLIENT.put(SCOREBOARD_TABLE_NAME, item)
    log.info(f"Wrote score to scoreboard: {game} - {first} {last} - {score} on {date_str}")


def get_daily_top_scores(game, date_str, limit=5):
    """
    Get top scores for a specific game and date from scoreboard table.

    :param game: Game name
    :param date_str: Date in YYYY-MM-DD format
    :param limit: Number of unique users to return
    :return: List of top scores for the day
    """
    # Query for all scores on this date for this game
    # The sort key starts with date, so we can use begins_with
    # Don't set a limit here since we need to deduplicate users
    key_condition = "game = :game AND begins_with(date_score_user, :date_prefix)"
    expression_values = {
        ":game": {"S": game},
        ":date_prefix": {"S": f"{date_str}#"},
    }

    items = CW_DYNAMO_CLIENT.query(
        SCOREBOARD_TABLE_NAME,
        key_condition,
        expression_values,
        scan_index_forward=True,  # Ascending order (but scores are inverted, so highest first)
    )

    # Deserialize and format the results
    top_scores = []
    seen_users = set()  # Track users to only show their best score of the day

    for item in items:
        score_item = deserialize_user(item)
        user_id = score_item.get("first_last")

        # Only include each user once (their highest score)
        if user_id not in seen_users:
            seen_users.add(user_id)
            first = score_item.get("first", "").title()
            last = score_item.get("last", "").title()
            score = int(score_item.get("score", 0))

            top_scores.append({
                "userName": f"{first} {last}",
                "score": score,
                "first": first,
                "last": last,
            })

            # Stop once we have enough unique users
            if len(top_scores) >= limit:
                break

    return top_scores


########################################################
# CWDynamo Client
########################################################
class CWDynamoClient:
    client = boto3.client("dynamodb")

    def get(self, table_name, key_expression):
        """Get an item from DynamoDB."""
        res = self.client.get_item(TableName=table_name, Key=key_expression)
        return res.get("Item")

    def get_all(self, table_name):
        """Scan all items from a DynamoDB table."""
        res = self.client.scan(TableName=table_name)
        return res.get("Items", [])

    def update(self, table_name, key_expression, field_value_map):
        """Update an item in DynamoDB."""
        update_expression_parts = []
        expression_attribute_values = {}

        for i, (field, value) in enumerate(field_value_map.items()):
            placeholder = f":val{i}"
            update_expression_parts.append(f"{field} = {placeholder}")

            if isinstance(value, str):
                expression_attribute_values[placeholder] = {"S": value}
            elif isinstance(value, int):
                expression_attribute_values[placeholder] = {"N": str(value)}
            elif isinstance(value, bool):
                expression_attribute_values[placeholder] = {"BOOL": value}
            elif isinstance(value, float):
                expression_attribute_values[placeholder] = {"N": str(value)}
            else:
                expression_attribute_values[placeholder] = {"S": str(value)}

        update_expression = "SET " + ", ".join(update_expression_parts)

        self.client.update_item(
            TableName=table_name,
            Key=key_expression,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
        )

    def put(self, table_name, item):
        """Put an item into DynamoDB."""
        self.client.put_item(TableName=table_name, Item=item)

    def query(self, table_name, key_condition_expression, expression_attribute_values, scan_index_forward=True, limit=None):
        """Query items from DynamoDB."""
        params = {
            "TableName": table_name,
            "KeyConditionExpression": key_condition_expression,
            "ExpressionAttributeValues": expression_attribute_values,
            "ScanIndexForward": scan_index_forward,
        }
        if limit:
            params["Limit"] = limit

        res = self.client.query(**params)
        return res.get("Items", [])


########################################################
# API Routes
########################################################
# More specific routes must come first
@app.get("/daphne/scoreboard/daily")
def get_daily_scoreboard():
    """
    Get top 5 scores for a specific date from the scoreboard table.
    Query params: game (required), date (optional, defaults to today in YYYY-MM-DD format)
    Returns: List of top 5 scores for that day sorted by score descending
    """
    try:
        game = app.current_event.get_query_string_value("game", "")
        date_param = app.current_event.get_query_string_value("date", "")

        # Validate game parameter
        if not game:
            return Response(
                status_code=400,
                content_type="application/json",
                body=json.dumps({"error": "Missing required query parameter: game"}),
            )

        if game not in GAME_NAMES:
            return Response(
                status_code=400,
                content_type="application/json",
                body=json.dumps({"error": f"Invalid game. Must be one of: {', '.join(GAME_NAMES.keys())}"}),
            )

        # Default to today if no date provided
        if not date_param:
            date_param = datetime.now().strftime("%Y-%m-%d")

        log.info(f"Fetching daily scoreboard for game: {game}, date: {date_param}")

        # Get daily top scores from scoreboard table
        top_scores = get_daily_top_scores(game, date_param, limit=5)

        log.info(f"Returning {len(top_scores)} daily scores for game: {game} on {date_param}")

        return Response(
            status_code=200,
            content_type="application/json",
            body=json.dumps({"date": date_param, "scores": top_scores}),
        )

    except Exception as e:
        log.exception(f"Error fetching daily scoreboard: {str(e)}")
        return Response(
            status_code=500,
            content_type="application/json",
            body=json.dumps({"error": "Failed to fetch daily scoreboard"}),
        )


@app.get("/daphne/scoreboard")
def get_scoreboard():
    """
    Get top 5 scores from the scoreboard by reading users with game-specific high_score field.
    Query params: game (required, values: "militsa" or "pritham")
    Returns: List of top 5 scores sorted by score descending
    """
    try:
        game = app.current_event.get_query_string_value("game", "")

        # Validate game parameter
        if not game:
            return Response(
                status_code=400,
                content_type="application/json",
                body=json.dumps({"error": "Missing required query parameter: game"}),
            )

        if game not in GAME_NAMES:
            return Response(
                status_code=400,
                content_type="application/json",
                body=json.dumps({"error": f"Invalid game. Must be one of: {', '.join(GAME_NAMES.keys())}"}),
            )

        log.info(f"Fetching scoreboard for game: {game}")

        # Get game-specific field name
        score_field = f"high_score_{game}"

        # Get all users
        raw_users = CW_DYNAMO_CLIENT.get_all(USER_TABLE_NAME)

        # Extract users with high scores (greater than 0)
        user_scores = []
        for raw_user in raw_users:
            user = deserialize_user(raw_user)
            if user and user.get(score_field) is not None:
                score = int(user.get(score_field, 0))
                if score > 0:  # Only include users who have actually played
                    # Extract first and last from first_last key
                    first_last = user.get("first_last", "_")
                    parts = first_last.split("_")
                    first = parts[0].title() if len(parts) > 0 else ""
                    last = parts[1].title() if len(parts) > 1 else ""

                    user_scores.append(
                        {
                            "userName": f"{first} {last}",
                            "score": score,
                            "first": first,
                            "last": last,
                        }
                    )

        # Sort by score descending and take top 5
        user_scores.sort(key=lambda x: x["score"], reverse=True)
        top_scores = user_scores[:5]

        log.info(f"Returning {len(top_scores)} scores for game: {game}")

        return Response(
            status_code=200,
            content_type="application/json",
            body=json.dumps(top_scores),
        )

    except Exception as e:
        log.exception(f"Error fetching scoreboard: {str(e)}")
        return Response(
            status_code=500,
            content_type="application/json",
            body=json.dumps({"error": "Failed to fetch scoreboard"}),
        )


@app.post("/daphne/score")
def submit_score():
    """
    Submit a new score. Only updates if it's a new high score for the user.
    Body: { "score": int, "first": str, "last": str, "game": str }
    """
    try:
        body = app.current_event.json_body
        score = body.get("score")
        first = body.get("first")
        last = body.get("last")
        game = body.get("game")

        if score is None or not first or not last or not game:
            return Response(
                status_code=400,
                content_type="application/json",
                body=json.dumps(
                    {"error": "Missing required fields: score, first, last, game"}
                ),
            )

        if game not in GAME_NAMES:
            return Response(
                status_code=400,
                content_type="application/json",
                body=json.dumps({"error": f"Invalid game. Must be one of: {', '.join(GAME_NAMES.keys())}"}),
            )

        first_last = f"{first.lower()}_{last.lower()}"
        game_name = GAME_NAMES[game]
        score_field = f"high_score_{game}"
        today_date = datetime.now().strftime("%Y-%m-%d")

        log.info(f"Checking score for {first} {last} in {game}: {score}")

        # Write ALL scores to scoreboard table (not just high scores)
        write_score_to_scoreboard(game, score, first_last, first, last, today_date)

        # Get existing user
        key_expression = {"first_last": {"S": first_last}}
        user_data = CW_DYNAMO_CLIENT.get(USER_TABLE_NAME, key_expression)

        if not user_data:
            log.warning(f"User not found: {first_last}")
            return Response(
                status_code=404,
                content_type="application/json",
                body=json.dumps({"error": "User not found"}),
            )

        user = deserialize_user(user_data)
        existing_high_score = user.get(score_field)

        # Convert Decimal to int if present
        if existing_high_score is not None:
            existing_high_score = int(existing_high_score)

        # Check if this is a new high score
        if existing_high_score is None or score > existing_high_score:
            # Get current scoreboard rankings before updating
            all_users = CW_DYNAMO_CLIENT.get_all(USER_TABLE_NAME)
            user_scores = get_user_scores_list(all_users, game)

            # Sort by score descending to get current rankings
            user_scores.sort(key=lambda x: x["score"], reverse=True)

            # Build old rankings map
            old_rankings = build_rankings_map(user_scores, top_n=5)

            # Update user with new high score
            CW_DYNAMO_CLIENT.update(
                USER_TABLE_NAME, key_expression, {score_field: score}
            )

            log.info(
                f"New high score for {first} {last} in {game}: {score} (previous: {existing_high_score})"
            )

            # Recalculate rankings with the new score
            user_scores = update_user_score_in_list(
                user_scores, first_last, score, first, last
            )

            # Re-sort with new score
            user_scores.sort(key=lambda x: x["score"], reverse=True)

            # Build new rankings (top 6 to catch person bumped to 6)
            new_rankings = build_rankings_map(user_scores, top_n=6)

            # Send text notification to the user who just scored
            send_text_notification(
                first_last,
                f"🎮 Congrats! You just set a new personal high score of {score} in {game_name}! 🎉",
            )

            # Notify anyone in top 5 who got bumped down
            notify_bumped_users(
                old_rankings, new_rankings, first_last, first, last, score, game_name
            )

            return Response(
                status_code=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "message": "New high score!",
                        "score": score,
                        "isHighScore": True,
                        "previousHighScore": existing_high_score,
                    }
                ),
            )
        else:
            log.info(
                f"Score {score} not higher than existing {existing_high_score} for {first} {last}"
            )

            return Response(
                status_code=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "message": "Score received but not a high score",
                        "score": score,
                        "isHighScore": False,
                        "currentHighScore": existing_high_score,
                    }
                ),
            )

    except Exception as e:
        log.exception(f"Error submitting score: {str(e)}")
        return Response(
            status_code=500,
            content_type="application/json",
            body=json.dumps({"error": "Failed to submit score"}),
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
        body=json.dumps({"message": "Route not found"}),
    )


@lambda_handler_decorator
def middleware_before(handler, event, context):
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

    # validate headers (optional for public scoreboard GET)
    first_last = event["headers"].get("x-first-last", "").lower()
    if first_last:
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


# Initialize clients at top level so connections are preserved between lambda calls
CW_DYNAMO_CLIENT = CWDynamoClient()
