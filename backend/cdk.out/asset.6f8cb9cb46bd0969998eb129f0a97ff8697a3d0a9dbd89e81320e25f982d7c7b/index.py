# NOTE: Return Type
#   As of AWS Lambda Validator V2, the following is an acceptable and expected return format:
#   { isAuthorized: boolean, context: dict }
#   Consequently, this will be the format returned in this lambda function.

import os
import traceback
import jwt

# Environment Variable
JWT_SECRET = os.environ["jwtSecret"]

# NOTE: Ideally being taken is as a configurable env var as well,
#       but hardcoded for now to save costs from Param Store
# Constants
GUEST_TOKEN_ACTION_LIST = ["secret", "cache_email"]
ADMIN_TOKEN_ACTION_LIST = [""]


########################################################
# Controller Action Handler
########################################################
def handler(event, context):
    try:
        # Peel action off of endpoint
        # NOTE: rawPath is of form "/controller/action"
        action = event["rawPath"].split("/")[-1]
        controller = event["rawPath"].split("/")[1]

        # Grab user_id from header (if present)
        user_id = event["headers"]["userId"]
    except Exception as e:
        error = {
            "context": str(e),
            "stack": traceback.format_exc(),
        }
        print(
            f"SERVER_ERROR: NiceGuy Failed to parse event into request format: {event} | Encountered error -- {error}"
        )
        return {
            "isAuthorized": False,
            "context": {
                "error": {
                    "message": f"SERVER_ERROR: Failed to parse event into request format: {event}",
                    "error": error,
                }
            },
        }

    # TODO: Parse out request body
    # TODO: Parse out query params

    # Successful parsing
    result = {
        "isAuthorized": True,
        # This is sent to the Lambda being fired, and follows this format:
        #   event["requestContext"]["authorizer"]["lambda"][YOUR_CONTEXT_KEY_HERE]
        "context": {
            "action": action,
            "user_id": user_id,
        },
    }
    print(result)
    return result
