import os
import json
import boto3
from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_certificatemanager as cert_manager,
    aws_lambda as lambdaFx,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ses as ses,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_apigatewayv2_alpha as apigw,
    CfnOutput,
)
from aws_cdk.aws_apigatewayv2_integrations_alpha import (
    HttpLambdaIntegration,
    HttpUrlIntegration,
)
from aws_cdk.aws_apigatewayv2_authorizers_alpha import (
    HttpLambdaResponseType,
    HttpLambdaAuthorizer,
)
from constructs import Construct


# (Dot Love Core Stack)
#   This stack covers the core pieces of the Dot Love infra. This includes:
#     * DotLove API Gateway
#     * Gizmo user Service and associated Databases
#     * Spectaculo Registry Service and associated Databases
#     * DotLove SES & support infra to handle notifications
class DotLoveCoreStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stack_env: str,
        ses_sns_arn: str,
        ses_sender_email: str,
        ses_admin_list: str,
        ssl_cert_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # NOTE: Staging env is dev backend with FE deployed to Netlify
        # Development environment (dev/prod)
        self.stack_env = stack_env

        ###################################################
        # SECRETS (stored in AWS SSM ParamStore)
        ###################################################
        boto_session = boto3.Session(profile_name="personal")
        self.ssm = boto_session.client("ssm", region_name="us-east-1")
        self.twilio_account_sid = self.obtain_ssm_client_secret(
            secret_name="/dot-love/twilio/account_sid"
        )
        # TODO: Make this dynamically take dev/prod based on config
        self.twilio_auth_token = self.obtain_ssm_client_secret(
            secret_name="/dot-love/twilio/auth-token/dev"
        )
        self.twilio_sender_number = self.obtain_ssm_client_secret(
            secret_name="/dot-love/twilio/sender-number"
        )
        self.contact_info = {
            "matthew": {
                "phone": self.obtain_ssm_client_secret(
                    secret_name="/dot-love/guests/contact/matthew/phone"
                ),
                "email": self.obtain_ssm_client_secret(
                    secret_name="/dot-love/guests/contact/matthew/email"
                ),
            },
            "mitzi": {
                "phone": self.obtain_ssm_client_secret(
                    secret_name="/dot-love/guests/contact/mitzi/phone"
                ),
                "email": self.obtain_ssm_client_secret(
                    secret_name="/dot-love/guests/contact/mitzi/email"
                ),
            },
        }

        ##################################################
        # DOMAIN SETUP
        ##################################################
        self.domain_cert = cert_manager.Certificate.from_certificate_arn(
            self, "dot_love_domain_cert", ssl_cert_arn
        )

        ###################################################
        # DATABASES (Dynamo)
        ###################################################
        # Create Users database
        self.dot_love_user_table = self.create_dot_love_user_table()
        # Create RegistryItem database
        self.dot_love_registry_item_table = self.create_dot_love_registry_item_table()
        # Create RegistryClaim database
        self.dot_love_registry_claim_table = self.create_dot_love_registry_claim_table()

        ###################################################
        # DOT LOVE API GATEWAY
        ###################################################
        # Create global dependency layer
        self.create_global_dependency_layer()

        # Create API Gateway
        self.dot_love_api_gw = self.create_dot_love_api_gw(ssl_cert=self.domain_cert)

        ###################################################
        # GIZMO USER SERVICE
        ###################################################
        # Create Gizmo Service Lambda and associate w/ API Gateway
        self.dot_love_gizmo_lambda = self.create_dot_love_gizmo_lambda(
            user_table=self.dot_love_user_table,
            ses_sender_email=ses_sender_email,
            ses_admin_list=ses_admin_list,
            twilio_auth_token=self.twilio_auth_token,
            twilio_account_sid=self.twilio_account_sid,
            twilio_sender_number=self.twilio_sender_number,
            contact_info=self.contact_info,
        )
        # Tie Gizmo Lambda to API Gateway
        self.add_gizmo_routes_to_api_gw(
            dot_love_api_gw=self.dot_love_api_gw,
            gizmo_lambda=self.dot_love_gizmo_lambda["function"],
        )

        ###################################################
        # SPECTACULO REGISTRY SERVICE
        ###################################################
        # Create Spectaculo Service Lambda and associate w/ API Gateway
        self.dot_love_spectaculo_lambda = self.create_dot_love_spectaculo_lambda(
            registry_item_table=self.dot_love_registry_item_table,
            registry_claim_table=self.dot_love_registry_claim_table,
        )
        # Tie Spectaculo Lambda to API Gateway
        self.add_spectaculo_routes_to_api_gw(
            dot_love_api_gw=self.dot_love_api_gw,
            spectaculo_lambda=self.dot_love_spectaculo_lambda["function"],
        )
        # Create s3 bucket to store registry item images
        self.create_dot_love_registry_item_img_s3()

        ###################################################
        # DOT LOVE EMAIL HANDLING (SES, SNS, S3, Lambda)
        ###################################################
        # Create S3 to store bounce and complaints
        self.dot_love_ses_s3 = self.create_dot_love_ses_s3()
        # Create Lambda to store bounce + complaints in S3
        self.dot_love_ses_lambda = self.create_dot_love_ses_lambda(
            self.dot_love_ses_s3, ses_sns_arn
        )
        # Initialize AmazonSES and grant Send permissions to the Gizmo Lambda
        self.dot_love_ses_config_set = self.create_dot_love_ses_config_set(
            self.dot_love_gizmo_lambda
        )

        ###################################################
        # DOT LOVE MEDIA ETC S3
        ###################################################
        # Create S3 to store bounce and complaints
        self.create_dot_love_website_media_etc_s3()

    ###################################################
    # DOT LOVE DATABASES
    ###################################################
    def create_dot_love_user_table(self):
        # Create User table
        user_table = dynamodb.Table(
            scope=self,
            id=f"{self.stack_env}-users",
            # PK: composite first_last
            partition_key=dynamodb.Attribute(
                name="first_last",
                type=dynamodb.AttributeType.STRING,
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
        )

        # Search users by guest link
        user_table.add_global_secondary_index(
            index_name="guest-link-lookup-index",
            partition_key=dynamodb.Attribute(
                name="guest_link",
                type=dynamodb.AttributeType.STRING,
            ),
        )

        return user_table

    def create_dot_love_registry_item_table(self):
        registry_item_table = dynamodb.Table(
            scope=self,
            id=f"{self.stack_env}-registry_items",
            # PK: id, a guid
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING,
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
        )

        return registry_item_table

    def create_dot_love_registry_claim_table(self):
        registry_claim_table = dynamodb.Table(
            scope=self,
            id=f"{self.stack_env}-registry_claims",
            # PK: id, a guid
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING,
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
        )

        # Search registry claim by claimant (composite first_last)
        registry_claim_table.add_global_secondary_index(
            index_name="claimant-lookup-index",
            partition_key=dynamodb.Attribute(
                name="first_last",
                type=dynamodb.AttributeType.STRING,
            ),
        )

        return registry_claim_table

    ###################################################
    # DOT LOVE SERVICES
    ###################################################
    def create_dot_love_gizmo_lambda(
        self,
        user_table,
        ses_sender_email,
        ses_admin_list,
        twilio_auth_token,
        twilio_account_sid,
        twilio_sender_number,
        contact_info,
    ):
        gizmo_lambda_role = iam.Role(
            scope=self,
            id=f"{self.stack_env}-dot-love-gizmo-service-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Lambda Role with access to User table",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # Grant db access
        user_table.grant_read_write_data(gizmo_lambda_role)

        gizmo_lambda = lambdaFx.Function(
            scope=self,
            id=f"{self.stack_env}-dot-love-gizmo-service",
            runtime=lambdaFx.Runtime.PYTHON_3_11,
            handler="index.handler",
            role=gizmo_lambda_role,
            code=lambdaFx.Code.from_asset("infra/lambda/gizmo/"),
            description="DotLove Gizmo Service, to handle user actions",
            environment={
                # Lambda Powertools
                "POWERTOOLS_SERVICE_NAME": "gizmo",
                "POWERTOOLS_LOG_LEVEL": "INFO",
                "TZ": "US/Eastern",
                # Resource ARNs
                "user_table_name": user_table.table_name,
                # SES Email config
                "ses_sender_email": ses_sender_email,
                "ses_admin_list": ses_admin_list,
                # twilio config
                "twilio_auth_token": twilio_auth_token,
                "twilio_account_sid": twilio_account_sid,
                "twilio_sender_number": twilio_sender_number,
                # contact info
                "mitzi_email": contact_info["mitzi"]["email"],
                "mitzi_phone": contact_info["mitzi"]["phone"],
                "matthew_email": contact_info["matthew"]["email"],
                "matthew_phone": contact_info["matthew"]["phone"],
            },
            layers=[self.global_lambda_layer],
            memory_size=512,
            timeout=Duration.seconds(15),
        )

        return {"function": gizmo_lambda, "role": gizmo_lambda_role}

    def create_dot_love_spectaculo_lambda(
        self,
        registry_item_table,
        registry_claim_table,
    ):
        spectaculo_lambda_role = iam.Role(
            scope=self,
            id=f"{self.stack_env}-dot-love-spectaculo-service-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Lambda Role with access to User table",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # Grant db access
        registry_item_table.grant_read_write_data(spectaculo_lambda_role)
        registry_claim_table.grant_read_write_data(spectaculo_lambda_role)

        spectaculo_lambda = lambdaFx.Function(
            scope=self,
            id=f"{self.stack_env}-dot-love-spectaculo-service",
            runtime=lambdaFx.Runtime.PYTHON_3_11,
            handler="index.handler",
            role=spectaculo_lambda_role,
            code=lambdaFx.Code.from_asset("infra/lambda/spectaculo/"),
            description="DotLove Spectaculo Service, to handle the registry",
            environment={
                # For getting registry data
                "registryItemTableName": registry_item_table.table_name,
                "registryClaimTableName": registry_claim_table.table_name,
                # Lambda Powertools
                "POWERTOOLS_SERVICE_NAME": "spectaculo",
                "POWERTOOLS_LOG_LEVEL": "INFO",
                "TZ": "US/Eastern",
            },
            layers=[self.global_lambda_layer],
            memory_size=512,
            timeout=Duration.seconds(15),
        )

        return {"function": spectaculo_lambda, "role": spectaculo_lambda_role}

    def create_dot_love_ses_lambda(self, dot_love_ses_s3, ses_sns_arn):
        # Create lambda Role
        ses_lambda_role = iam.Role(
            scope=self,
            id=f"{self.stack_env}-dot-love-ses-notif-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="SES Notification Lambda Role",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaVPCAccessExecutionRole"
                ),
            ],
        )

        # Grant s3 write access
        dot_love_ses_s3["bucket"].grant_read_write(ses_lambda_role)

        # Create lambda
        ses_lambda = lambdaFx.Function(
            scope=self,
            id=f"{self.stack_env}-dot-love-ses-notif-lambda",
            runtime=lambdaFx.Runtime.PYTHON_3_11,
            handler="index.handler",
            role=ses_lambda_role,
            code=lambdaFx.Code.from_asset("infra/lambda/ses/"),  # TODO:
            description="DotLove SES Notification Lambda, to handle: Bounce, Received, and Compliant notifications",
            environment={
                "ses_s3_bucket_name": dot_love_ses_s3["bucket"].bucket_name,
            },
            timeout=Duration.seconds(15),
        )

        # Subscribe lambda to SES Topic that notifies of email Received/Bounce/Complaint
        topic = sns.Topic.from_topic_arn(
            self,
            id="dot-love-ses-notif-sns",
            topic_arn=ses_sns_arn,
        )
        topic.add_subscription(subscriptions.LambdaSubscription(ses_lambda))

        return {"function": ses_lambda, "role": ses_lambda_role}

    ###################################################
    # DOT LOVE API GATEWAY ORCHESTRATION
    ###################################################
    def create_dot_love_api_gw(self, ssl_cert):
        domain_name = apigw.DomainName(
            scope=self,
            id=f"{self.stack_env}-domain-name",
            domain_name="api.mitzimatthew.love",
            certificate=ssl_cert,
        )

        # Create DotLove API Gateway
        dot_love_api = apigw.HttpApi(
            scope=self,
            id=f"{self.stack_env}-dot-love-api",
            description="DotLove API Gateway",
            cors_preflight=apigw.CorsPreflightOptions(
                allow_headers=["*"],
                allow_methods=[
                    apigw.CorsHttpMethod.GET,
                    apigw.CorsHttpMethod.HEAD,
                    apigw.CorsHttpMethod.OPTIONS,
                    apigw.CorsHttpMethod.POST,
                ],
                # NOTE: Should be fine for the calls I make from Spectaculo to Gizmo, we'll see
                allow_origins=["*"],
                max_age=Duration.days(10),
            ),
        )
        main_api_stage = apigw.HttpStage(
            scope=self,
            id=f"{self.stack_env}-dot-love-api-stage",
            http_api=dot_love_api,
            stage_name="prod",
            auto_deploy=True,
            domain_mapping=apigw.DomainMappingOptions(domain_name=domain_name),
        )

        # this is needed for the cname record!!!
        # Host: api
        # Value: this value
        CfnOutput(
            self,
            "RegionalDomainName",
            value=domain_name.regional_domain_name,
            description="regional domain name for mitzimatthew.love",
        )

        return dot_love_api

    def add_gizmo_routes_to_api_gw(self, dot_love_api_gw, gizmo_lambda):
        # Create DotLove Gizmo Service lambda association
        gizmo_service_integration = HttpLambdaIntegration(
            f"{self.stack_env}-dot-love-gizmo-service", gizmo_lambda
        )

        # Create Gizmo API routes
        #
        # Health check
        dot_love_api_gw.add_routes(
            path="/gizmo/ping",
            methods=[apigw.HttpMethod.GET],
            integration=gizmo_service_integration,
        )
        #
        # Login a user
        dot_love_api_gw.add_routes(
            path="/gizmo/user",
            methods=[apigw.HttpMethod.GET],
            integration=gizmo_service_integration,
        )
        #
        # Register a new user
        dot_love_api_gw.add_routes(
            path="/gizmo/user",
            methods=[apigw.HttpMethod.POST],
            integration=gizmo_service_integration,
        )
        #
        # Update a user's info
        dot_love_api_gw.add_routes(
            path="/gizmo/user",
            methods=[apigw.HttpMethod.PATCH],
            integration=gizmo_service_integration,
        )
        #
        # Get user by guest link, using a query param (?code={})
        dot_love_api_gw.add_routes(
            path="/gizmo/user/guest",
            methods=[apigw.HttpMethod.GET],
            integration=gizmo_service_integration,
        )
        #
        # Email a user
        dot_love_api_gw.add_routes(
            path="/gizmo/email",
            methods=[apigw.HttpMethod.POST],
            integration=gizmo_service_integration,
        )
        #
        # Text a user
        dot_love_api_gw.add_routes(
            path="/gizmo/text",
            methods=[apigw.HttpMethod.POST],
            integration=gizmo_service_integration,
        )

        return

    def add_spectaculo_routes_to_api_gw(self, dot_love_api_gw, spectaculo_lambda):
        # Create DotLove Spetaculo Service lambda association
        spectaculo_service_integration = HttpLambdaIntegration(
            f"{self.stack_env}-dot-love-spectaculo-service", spectaculo_lambda
        )

        # Create Spectaculo API routes
        #
        # /claim/create
        # Create a registry claim
        dot_love_api_gw.add_routes(
            path="/spectaculo/claim/create",
            methods=[apigw.HttpMethod.POST],
            integration=spectaculo_service_integration,
            # TODO: Add this? for common mesage format
            # authorizer=self.lambda_authorizer,
        )
        #
        # /claim/update
        # Update a registry claim
        dot_love_api_gw.add_routes(
            path="/spectaculo/claim/update",
            methods=[apigw.HttpMethod.PATCH],
            integration=spectaculo_service_integration,
            # TODO: Add this? for common mesage format
            # authorizer=self.lambda_authorizer,
        )

        return

    ###################################################
    # SES Config
    ###################################################
    def create_dot_love_ses_config_set(self, dot_love_gizmo_lambda):
        ses_config_set = ses.ConfigurationSet(
            self,
            f"{self.stack_env}-dot-love-gizmo-ses-configuration-set",
        )

        # Grant lambda role ses perms & share ses_id to function
        dot_love_gizmo_lambda["role"].attach_inline_policy(
            iam.Policy(
                self,
                f"{self.stack_env}-ses-policy",
                statements=[
                    iam.PolicyStatement(
                        actions=[
                            "ses:SendEmail",
                            "ses:SendTemplatedEmail",
                            "ses:SendRawEmail",
                            "ses:SendBulkTemplatedEmail",
                        ],
                        resources=["*"],
                    )
                ],
            )
        )

        # Add SES ID to Gizmo Service environment variables
        dot_love_gizmo_lambda["function"].add_environment(
            key="ses_config_id", value=ses_config_set.configuration_set_name
        )

        return ses_config_set

    ###################################################
    # DOT LOVE BUCKETS
    ###################################################
    def create_dot_love_ses_s3(self):
        lifecycle_rule = s3.LifecycleRule(
            id=f"{self.stack_env}-ses-notif-rule",
            expiration=Duration.days(30),
        )
        ses_s3_bucket = s3.Bucket(
            scope=self,
            id=f"{self.stack_env}-dot-love-ses-notif-s3",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            lifecycle_rules=[lifecycle_rule],
        )

        return {"bucket": ses_s3_bucket}

    def create_dot_love_registry_item_img_s3(self):
        registry_item_img_bucket = s3.Bucket(
            scope=self,
            id=f"{self.stack_env}-dot-love-registry-item-img-s3",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

        return {"bucket": registry_item_img_bucket}

    def create_dot_love_website_media_etc_s3(self):
        website_media_etc_bucket = s3.Bucket(
            scope=self,
            id=f"{self.stack_env}-dot-love-website-media-etc-s3",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

        return {"bucket": website_media_etc_bucket}

    def obtain_ssm_client_secret(self, secret_name):
        secret = self.ssm.get_parameter(Name=secret_name, WithDecryption=True)
        return secret["Parameter"]["Value"]

    def create_global_dependency_layer(self):
        # External Package(s) (AWS Powertools, Twilio)
        # NOTE: Generation guide:
        #   https://medium.com/geekculture/deploying-aws-lambda-layers-with-python-8b15e24bdad2
        #   So essentially, creating a `layer` folder, and running the following:
        #   pip3 install -r ~/code/dot-love/backend/infra/lambda/gizmo/requirements.txt --target ~/code/dot-love/backend/infra/lambda/gizmo/layer/python/lib/python3.11/site-packages
        self.global_lambda_layer = lambdaFx.LayerVersion(
            self,
            f"{self.stack_env}-global-layer",
            code=lambdaFx.AssetCode("infra/lambda/gizmo/layer/"),
            compatible_runtimes=[lambdaFx.Runtime.PYTHON_3_11],
        )
