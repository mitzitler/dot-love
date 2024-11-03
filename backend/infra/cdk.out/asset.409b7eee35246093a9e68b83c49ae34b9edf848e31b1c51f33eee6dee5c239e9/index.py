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

        # Grab JWT from header
        encoded_jwt = event["headers"]["authorization"]
    except Exception as e:
        error = {
            "context": str(e),
            "stack": traceback.format_exc(),
        }
        print(
            f"SERVER_ERROR: Failed to parse event into request format: {event} | Encountered error -- {error}"
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

    # JWT Validation
    try:
        # Decode, using secret
        jwt_payload = jwt.decode(encoded_jwt, JWT_SECRET, algorithms=["HS256"])

        # Ensure this is indeed an AuthToken, and not a Refresh
        if jwt_payload["type"] == "refresh":
            raise Exception("Refresh token provided in header, instead of Auth token")

        # Decline GuestTokens, with exceptions
        if jwt_payload["type"] == "guest":
            if action not in GUEST_TOKEN_ACTION_LIST:
                raise Exception(
                    "Refresh token provided in header, instead of Auth token"
                )

        # Handle admin users
        if controller == "admin":
            # TODO: Admin check
            #       No admin routes as of now, so no need to flesh this out atm
            #       For now, just return an exception
            raise Exception("Admin controller not accounted for in Validator Lambda")

    except Exception as e:
        error = {
            "context": str(e),
            "stack": traceback.format_exc(),
        }
        print(f"SERVER_ERROR: Validator encountered unhandled error -- {error}")
        return {
            "isAuthorized": False,
            "context": {
                "error": {
                    "message": "SERVER_ERROR: Validator encountered unhandled error",
                    "error": error,
                }
            },
        }

    # Successful validation
    result = {
        "isAuthorized": True,
        # This is sent to the Lambda being fired, and follows this format:
        #   event["requestContext"]["authorizer"]["lambda"][YOUR_CONTEXT_KEY_HERE]
        "context": {
            "action": action,
            "user_id": jwt_payload["sub"],
            "user_type": jwt_payload["role"],
        },
    }
    print(result)
    return result
