#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infra.dot_love_core_stack import DotLoveCoreStack

app = cdk.App()

config = app.node.try_get_context("config")

# General config
account_id = config["account_id"]
region = config["region"]
stack_env = config["stack_env"]

# SES Config
ses_sns_arn = config["ses_sns_arn"]
ses_sender_email = config["ses_sender_email"]
ses_admin_list = config["ses_admin_list"]
api_ssl_cert_arn = config["api_ssl_cert_arn"]
cdn_ssl_cert_arn = config["cdn_ssl_cert_arn"]

dotLoveStack = DotLoveCoreStack(
    scope=app,
    construct_id=f"{stack_env}-dot-love-stack",
    env=cdk.Environment(account=account_id, region=region),
    stack_env=stack_env,
    ses_sns_arn=ses_sns_arn,
    ses_sender_email=ses_sender_email,
    ses_admin_list=ses_admin_list,
    api_ssl_cert_arn=api_ssl_cert_arn,
    cdn_ssl_cert_arn=cdn_ssl_cert_arn,
)

app.synth()
