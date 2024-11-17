import os
import json
import traceback
import stripe
import boto3
import hashlib
import logging
from enum import Enum
from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.idempotency import (
    DynamoDBPersistenceLayer,
    IdempotencyConfig,
    idempotent_function,
)

########################################################
# Controller Action Handler
########################################################


@log.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_HTTP, log_event=True
)
def handler(event, context):
    res = "sample"
    return res
