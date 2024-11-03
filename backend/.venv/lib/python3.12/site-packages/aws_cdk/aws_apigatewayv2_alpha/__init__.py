'''
# AWS::APIGatewayv2 Construct Library

<!--BEGIN STABILITY BANNER-->---


Features                                   | Stability
-------------------------------------------|--------------------------------------------------------
Higher level constructs for HTTP APIs      | ![Experimental](https://img.shields.io/badge/experimental-important.svg?style=for-the-badge)
Higher level constructs for Websocket APIs | ![Experimental](https://img.shields.io/badge/experimental-important.svg?style=for-the-badge)

> **Experimental:** Higher level constructs in this module that are marked as experimental are
> under active development. They are subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model and
> breaking changes will be announced in the release notes. This means that while you may use them,
> you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

## Table of Contents

* [Introduction](#introduction)
* [HTTP API](#http-api)

  * [Defining HTTP APIs](#defining-http-apis)
  * [Cross Origin Resource Sharing (CORS)](#cross-origin-resource-sharing-cors)
  * [Publishing HTTP APIs](#publishing-http-apis)
  * [Custom Domain](#custom-domain)
  * [Mutual TLS](#mutual-tls-mtls)
  * [Managing access to HTTP APIs](#managing-access-to-http-apis)
  * [Metrics](#metrics)
  * [VPC Link](#vpc-link)
  * [Private Integration](#private-integration)
* [WebSocket API](#websocket-api)

  * [Manage Connections Permission](#manage-connections-permission)
  * [Managing access to WebSocket APIs](#managing-access-to-websocket-apis)

## Introduction

Amazon API Gateway is an AWS service for creating, publishing, maintaining, monitoring, and securing REST, HTTP, and WebSocket
APIs at any scale. API developers can create APIs that access AWS or other web services, as well as data stored in the AWS Cloud.
As an API Gateway API developer, you can create APIs for use in your own client applications. Read the
[Amazon API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html).

This module supports features under [API Gateway v2](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_ApiGatewayV2.html)
that lets users set up Websocket and HTTP APIs.
REST APIs can be created using the `@aws-cdk/aws-apigateway` module.

## HTTP API

HTTP APIs enable creation of RESTful APIs that integrate with AWS Lambda functions, known as Lambda proxy integration,
or to any routable HTTP endpoint, known as HTTP proxy integration.

### Defining HTTP APIs

HTTP APIs have two fundamental concepts - Routes and Integrations.

Routes direct incoming API requests to backend resources. Routes consist of two parts: an HTTP method and a resource
path, such as, `GET /books`. Learn more at [Working with
routes](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-routes.html). Use the `ANY` method
to match any methods for a route that are not explicitly defined.

Integrations define how the HTTP API responds when a client reaches a specific Route. HTTP APIs support Lambda proxy
integration, HTTP proxy integration and, AWS service integrations, also known as private integrations. Learn more at
[Configuring integrations](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations.html).

Integrations are available at the `aws-apigatewayv2-integrations` module and more information is available in that module.
As an early example, the following code snippet configures a route `GET /books` with an HTTP proxy integration all
configures all other HTTP method calls to `/books` to a lambda proxy.

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration, HttpLambdaIntegration

# books_default_fn: lambda.Function


get_books_integration = HttpUrlIntegration("GetBooksIntegration", "https://get-books-proxy.example.com")
books_default_integration = HttpLambdaIntegration("BooksIntegration", books_default_fn)

http_api = apigwv2.HttpApi(self, "HttpApi")

http_api.add_routes(
    path="/books",
    methods=[apigwv2.HttpMethod.GET],
    integration=get_books_integration
)
http_api.add_routes(
    path="/books",
    methods=[apigwv2.HttpMethod.ANY],
    integration=books_default_integration
)
```

The URL to the endpoint can be retrieved via the `apiEndpoint` attribute. By default this URL is enabled for clients. Use `disableExecuteApiEndpoint` to disable it.

```python
http_api = apigwv2.HttpApi(self, "HttpApi",
    disable_execute_api_endpoint=True
)
```

The `defaultIntegration` option while defining HTTP APIs lets you create a default catch-all integration that is
matched when a client reaches a route that is not explicitly defined.

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration


apigwv2.HttpApi(self, "HttpProxyApi",
    default_integration=HttpUrlIntegration("DefaultIntegration", "https://example.com")
)
```

### Cross Origin Resource Sharing (CORS)

[Cross-origin resource sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) is a browser security
feature that restricts HTTP requests that are initiated from scripts running in the browser. Enabling CORS will allow
requests to your API from a web application hosted in a domain different from your API domain.

When configured CORS for an HTTP API, API Gateway automatically sends a response to preflight `OPTIONS` requests, even
if there isn't an `OPTIONS` route configured. Note that, when this option is used, API Gateway will ignore CORS headers
returned from your backend integration. Learn more about [Configuring CORS for an HTTP
API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-cors.html).

The `corsPreflight` option lets you specify a CORS configuration for an API.

```python
apigwv2.HttpApi(self, "HttpProxyApi",
    cors_preflight=apigwv2.CorsPreflightOptions(
        allow_headers=["Authorization"],
        allow_methods=[apigwv2.CorsHttpMethod.GET, apigwv2.CorsHttpMethod.HEAD, apigwv2.CorsHttpMethod.OPTIONS, apigwv2.CorsHttpMethod.POST
        ],
        allow_origins=["*"],
        max_age=Duration.days(10)
    )
)
```

### Publishing HTTP APIs

A Stage is a logical reference to a lifecycle state of your API (for example, `dev`, `prod`, `beta`, or `v2`). API
stages are identified by their stage name. Each stage is a named reference to a deployment of the API made available for
client applications to call.

Use `HttpStage` to create a Stage resource for HTTP APIs. The following code sets up a Stage, whose URL is available at
`https://{api_id}.execute-api.{region}.amazonaws.com/beta`.

```python
# api: apigwv2.HttpApi


apigwv2.HttpStage(self, "Stage",
    http_api=api,
    stage_name="beta"
)
```

If you omit the `stageName` will create a `$default` stage. A `$default` stage is one that is served from the base of
the API's URL - `https://{api_id}.execute-api.{region}.amazonaws.com/`.

Note that, `HttpApi` will always creates a `$default` stage, unless the `createDefaultStage` property is unset.

### Custom Domain

Custom domain names are simpler and more intuitive URLs that you can provide to your API users. Custom domain name are associated to API stages.

The code snippet below creates a custom domain and configures a default domain mapping for your API that maps the
custom domain to the `$default` stage of the API.

```python
import aws_cdk.aws_certificatemanager as acm
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration

# handler: lambda.Function


cert_arn = "arn:aws:acm:us-east-1:111111111111:certificate"
domain_name = "example.com"

dn = apigwv2.DomainName(self, "DN",
    domain_name=domain_name,
    certificate=acm.Certificate.from_certificate_arn(self, "cert", cert_arn)
)
api = apigwv2.HttpApi(self, "HttpProxyProdApi",
    default_integration=HttpLambdaIntegration("DefaultIntegration", handler),
    # https://${dn.domainName}/foo goes to prodApi $default stage
    default_domain_mapping=apigwv2.DomainMappingOptions(
        domain_name=dn,
        mapping_key="foo"
    )
)
```

To migrate a domain endpoint from one type to another, you can add a new endpoint configuration via `addEndpoint()`
and then configure DNS records to route traffic to the new endpoint. After that, you can remove the previous endpoint configuration.
Learn more at [Migrating a custom domain name](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-regional-api-custom-domain-migrate.html)

To associate a specific `Stage` to a custom domain mapping -

```python
# api: apigwv2.HttpApi
# dn: apigwv2.DomainName


api.add_stage("beta",
    stage_name="beta",
    auto_deploy=True,
    # https://${dn.domainName}/bar goes to the beta stage
    domain_mapping=apigwv2.DomainMappingOptions(
        domain_name=dn,
        mapping_key="bar"
    )
)
```

The same domain name can be associated with stages across different `HttpApi` as so -

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration

# handler: lambda.Function
# dn: apigwv2.DomainName


api_demo = apigwv2.HttpApi(self, "DemoApi",
    default_integration=HttpLambdaIntegration("DefaultIntegration", handler),
    # https://${dn.domainName}/demo goes to apiDemo $default stage
    default_domain_mapping=apigwv2.DomainMappingOptions(
        domain_name=dn,
        mapping_key="demo"
    )
)
```

The `mappingKey` determines the base path of the URL with the custom domain. Each custom domain is only allowed
to have one API mapping with undefined `mappingKey`. If more than one API mappings are specified, `mappingKey` will be required for all of them. In the sample above, the custom domain is associated
with 3 API mapping resources across different APIs and Stages.

|        API     |     Stage   |   URL  |
| :------------: | :---------: | :----: |
| api | $default  |   `https://${domainName}/foo`  |
| api | beta  |   `https://${domainName}/bar`  |
| apiDemo | $default  |   `https://${domainName}/demo`  |

You can retrieve the full domain URL with mapping key using the `domainUrl` property as so -

```python
# api_demo: apigwv2.HttpApi

demo_domain_url = api_demo.default_stage.domain_url
```

### Mutual TLS (mTLS)

Mutual TLS can be configured to limit access to your API based by using client certificates instead of (or as an extension of) using authorization headers.

```python
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_certificatemanager as acm
# bucket: s3.Bucket


cert_arn = "arn:aws:acm:us-east-1:111111111111:certificate"
domain_name = "example.com"

apigwv2.DomainName(self, "DomainName",
    domain_name=domain_name,
    certificate=acm.Certificate.from_certificate_arn(self, "cert", cert_arn),
    mtls=apigwv2.MTLSConfig(
        bucket=bucket,
        key="someca.pem",
        version="version"
    )
)
```

Instructions for configuring your trust store can be found [here](https://aws.amazon.com/blogs/compute/introducing-mutual-tls-authentication-for-amazon-api-gateway/)

### Managing access to HTTP APIs

API Gateway supports multiple mechanisms for [controlling and managing access to your HTTP
API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-access-control.html) through authorizers.

These authorizers can be found in the [APIGatewayV2-Authorizers](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-apigatewayv2-authorizers-readme.html) constructs library.

### Metrics

The API Gateway v2 service sends metrics around the performance of HTTP APIs to Amazon CloudWatch.
These metrics can be referred to using the metric APIs available on the `HttpApi` construct.
The APIs with the `metric` prefix can be used to get reference to specific metrics for this API. For example,
the method below refers to the client side errors metric for this API.

```python
api = apigwv2.HttpApi(self, "my-api")
client_error_metric = api.metric_client_error()
```

Please note that this will return a metric for all the stages defined in the api. It is also possible to refer to metrics for a specific Stage using
the `metric` methods from the `Stage` construct.

```python
api = apigwv2.HttpApi(self, "my-api")
stage = apigwv2.HttpStage(self, "Stage",
    http_api=api
)
client_error_metric = stage.metric_client_error()
```

### VPC Link

Private integrations let HTTP APIs connect with AWS resources that are placed behind a VPC. These are usually Application
Load Balancers, Network Load Balancers or a Cloud Map service. The `VpcLink` construct enables this integration.
The following code creates a `VpcLink` to a private VPC.

```python
import aws_cdk.aws_ec2 as ec2


vpc = ec2.Vpc(self, "VPC")
vpc_link = apigwv2.VpcLink(self, "VpcLink", vpc=vpc)
```

Any existing `VpcLink` resource can be imported into the CDK app via the `VpcLink.fromVpcLinkAttributes()`.

```python
import aws_cdk.aws_ec2 as ec2

# vpc: ec2.Vpc

awesome_link = apigwv2.VpcLink.from_vpc_link_attributes(self, "awesome-vpc-link",
    vpc_link_id="us-east-1_oiuR12Abd",
    vpc=vpc
)
```

### Private Integration

Private integrations enable integrating an HTTP API route with private resources in a VPC, such as Application Load Balancers or
Amazon ECS container-based applications.  Using private integrations, resources in a VPC can be exposed for access by
clients outside of the VPC.

These integrations can be found in the [aws-apigatewayv2-integrations](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-apigatewayv2-integrations-readme.html) constructs library.

## WebSocket API

A WebSocket API in API Gateway is a collection of WebSocket routes that are integrated with backend HTTP endpoints,
Lambda functions, or other AWS services. You can use API Gateway features to help you with all aspects of the API
lifecycle, from creation through monitoring your production APIs. [Read more](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api-overview.html)

WebSocket APIs have two fundamental concepts - Routes and Integrations.

WebSocket APIs direct JSON messages to backend integrations based on configured routes. (Non-JSON messages are directed
to the configured `$default` route.)

Integrations define how the WebSocket API behaves when a client reaches a specific Route. Learn more at
[Configuring integrations](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api-integration-requests.html).

Integrations are available in the `aws-apigatewayv2-integrations` module and more information is available in that module.

To add the default WebSocket routes supported by API Gateway (`$connect`, `$disconnect` and `$default`), configure them as part of api props:

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration

# connect_handler: lambda.Function
# disconnect_handler: lambda.Function
# default_handler: lambda.Function


web_socket_api = apigwv2.WebSocketApi(self, "mywsapi",
    connect_route_options=apigwv2.WebSocketRouteOptions(integration=WebSocketLambdaIntegration("ConnectIntegration", connect_handler)),
    disconnect_route_options=apigwv2.WebSocketRouteOptions(integration=WebSocketLambdaIntegration("DisconnectIntegration", disconnect_handler)),
    default_route_options=apigwv2.WebSocketRouteOptions(integration=WebSocketLambdaIntegration("DefaultIntegration", default_handler))
)

apigwv2.WebSocketStage(self, "mystage",
    web_socket_api=web_socket_api,
    stage_name="dev",
    auto_deploy=True
)
```

To retrieve a websocket URL and a callback URL:

```python
# web_socket_stage: apigwv2.WebSocketStage


web_socket_uRL = web_socket_stage.url
# wss://${this.api.apiId}.execute-api.${s.region}.${s.urlSuffix}/${urlPath}
callback_uRL = web_socket_stage.callback_url
```

To add any other route:

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration

# message_handler: lambda.Function

web_socket_api = apigwv2.WebSocketApi(self, "mywsapi")
web_socket_api.add_route("sendmessage",
    integration=WebSocketLambdaIntegration("SendMessageIntegration", message_handler)
)
```

To import an existing WebSocketApi:

```python
web_socket_api = apigwv2.WebSocketApi.from_web_socket_api_attributes(self, "mywsapi", web_socket_id="api-1234")
```

### Manage Connections Permission

Grant permission to use API Gateway Management API of a WebSocket API by calling the `grantManageConnections` API.
You can use Management API to send a callback message to a connected client, get connection information, or disconnect the client. Learn more at [Use @connections commands in your backend service](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-how-to-call-websocket-api-connections.html).

```python
# fn: lambda.Function


web_socket_api = apigwv2.WebSocketApi(self, "mywsapi")
stage = apigwv2.WebSocketStage(self, "mystage",
    web_socket_api=web_socket_api,
    stage_name="dev"
)
# per stage permission
stage.grant_management_api_access(fn)
# for all the stages permission
web_socket_api.grant_manage_connections(fn)
```

### Managing access to WebSocket APIs

API Gateway supports multiple mechanisms for [controlling and managing access to a WebSocket API](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api-control-access.html) through authorizers.

These authorizers can be found in the [APIGatewayV2-Authorizers](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-apigatewayv2-authorizers-readme.html) constructs library.

### API Keys

Websocket APIs also support usage of API Keys. An API Key is a key that is used to grant access to an API. These are useful for controlling and tracking access to an API, when used together with [usage plans](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-api-usage-plans.html). These together allow you to configure controls around API access such as quotas and throttling, along with per-API Key metrics on usage.

To require an API Key when accessing the Websocket API:

```python
web_socket_api = apigwv2.WebSocketApi(self, "mywsapi",
    api_key_selection_expression=apigwv2.WebSocketApiKeySelectionExpression.HEADER_X_API_KEY
)
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.ApiMappingAttributes",
    jsii_struct_bases=[],
    name_mapping={"api_mapping_id": "apiMappingId"},
)
class ApiMappingAttributes:
    def __init__(self, *, api_mapping_id: builtins.str) -> None:
        '''(experimental) The attributes used to import existing ApiMapping.

        :param api_mapping_id: (experimental) The API mapping ID.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            api_mapping_attributes = apigatewayv2_alpha.ApiMappingAttributes(
                api_mapping_id="apiMappingId"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__742c0d28ff28876a0bc0d1152ef7b3343151f193a0e128ba64a6cbc4509c8f05)
            check_type(argname="argument api_mapping_id", value=api_mapping_id, expected_type=type_hints["api_mapping_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_mapping_id": api_mapping_id,
        }

    @builtins.property
    def api_mapping_id(self) -> builtins.str:
        '''(experimental) The API mapping ID.

        :stability: experimental
        '''
        result = self._values.get("api_mapping_id")
        assert result is not None, "Required property 'api_mapping_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiMappingAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.ApiMappingProps",
    jsii_struct_bases=[],
    name_mapping={
        "api": "api",
        "domain_name": "domainName",
        "api_mapping_key": "apiMappingKey",
        "stage": "stage",
    },
)
class ApiMappingProps:
    def __init__(
        self,
        *,
        api: "IApi",
        domain_name: "IDomainName",
        api_mapping_key: typing.Optional[builtins.str] = None,
        stage: typing.Optional["IStage"] = None,
    ) -> None:
        '''(experimental) Properties used to create the ApiMapping resource.

        :param api: (experimental) The Api to which this mapping is applied.
        :param domain_name: (experimental) custom domain name of the mapping target.
        :param api_mapping_key: (experimental) Api mapping key. The path where this stage should be mapped to on the domain Default: - undefined for the root path mapping.
        :param stage: (experimental) stage for the ApiMapping resource required for WebSocket API defaults to default stage of an HTTP API. Default: - Default stage of the passed API for HTTP API, required for WebSocket API

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            # api: apigatewayv2_alpha.IApi
            # domain_name: apigatewayv2_alpha.DomainName
            # stage: apigatewayv2_alpha.IStage
            
            api_mapping_props = apigatewayv2_alpha.ApiMappingProps(
                api=api,
                domain_name=domain_name,
            
                # the properties below are optional
                api_mapping_key="apiMappingKey",
                stage=stage
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75ffb83f83ec42f2a0382885c05d069ecb32c50d82d796df38b991d84782ded6)
            check_type(argname="argument api", value=api, expected_type=type_hints["api"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument api_mapping_key", value=api_mapping_key, expected_type=type_hints["api_mapping_key"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api": api,
            "domain_name": domain_name,
        }
        if api_mapping_key is not None:
            self._values["api_mapping_key"] = api_mapping_key
        if stage is not None:
            self._values["stage"] = stage

    @builtins.property
    def api(self) -> "IApi":
        '''(experimental) The Api to which this mapping is applied.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast("IApi", result)

    @builtins.property
    def domain_name(self) -> "IDomainName":
        '''(experimental) custom domain name of the mapping target.

        :stability: experimental
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast("IDomainName", result)

    @builtins.property
    def api_mapping_key(self) -> typing.Optional[builtins.str]:
        '''(experimental) Api mapping key.

        The path where this stage should be mapped to on the domain

        :default: - undefined for the root path mapping.

        :stability: experimental
        '''
        result = self._values.get("api_mapping_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stage(self) -> typing.Optional["IStage"]:
        '''(experimental) stage for the ApiMapping resource required for WebSocket API defaults to default stage of an HTTP API.

        :default: - Default stage of the passed API for HTTP API, required for WebSocket API

        :stability: experimental
        '''
        result = self._values.get("stage")
        return typing.cast(typing.Optional["IStage"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiMappingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.AuthorizerPayloadVersion")
class AuthorizerPayloadVersion(enum.Enum):
    '''(experimental) Payload format version for lambda authorizers.

    :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html
    :stability: experimental
    '''

    VERSION_1_0 = "VERSION_1_0"
    '''(experimental) Version 1.0.

    :stability: experimental
    '''
    VERSION_2_0 = "VERSION_2_0"
    '''(experimental) Version 2.0.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.BatchHttpRouteOptions",
    jsii_struct_bases=[],
    name_mapping={"integration": "integration"},
)
class BatchHttpRouteOptions:
    def __init__(self, *, integration: "HttpRouteIntegration") -> None:
        '''(experimental) Options used when configuring multiple routes, at once.

        The options here are the ones that would be configured for all being set up.

        :param integration: (experimental) The integration to be configured on this route.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            # http_route_integration: apigatewayv2_alpha.HttpRouteIntegration
            
            batch_http_route_options = apigatewayv2_alpha.BatchHttpRouteOptions(
                integration=http_route_integration
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd6be8693e2cd2875856654344853bc620de9c6dd3e82fbd384cba9b5468a36d)
            check_type(argname="argument integration", value=integration, expected_type=type_hints["integration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration": integration,
        }

    @builtins.property
    def integration(self) -> "HttpRouteIntegration":
        '''(experimental) The integration to be configured on this route.

        :stability: experimental
        '''
        result = self._values.get("integration")
        assert result is not None, "Required property 'integration' is missing"
        return typing.cast("HttpRouteIntegration", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchHttpRouteOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.CorsHttpMethod")
class CorsHttpMethod(enum.Enum):
    '''(experimental) Supported CORS HTTP methods.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        apigwv2.HttpApi(self, "HttpProxyApi",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_headers=["Authorization"],
                allow_methods=[apigwv2.CorsHttpMethod.GET, apigwv2.CorsHttpMethod.HEAD, apigwv2.CorsHttpMethod.OPTIONS, apigwv2.CorsHttpMethod.POST
                ],
                allow_origins=["*"],
                max_age=Duration.days(10)
            )
        )
    '''

    ANY = "ANY"
    '''(experimental) HTTP ANY.

    :stability: experimental
    '''
    DELETE = "DELETE"
    '''(experimental) HTTP DELETE.

    :stability: experimental
    '''
    GET = "GET"
    '''(experimental) HTTP GET.

    :stability: experimental
    '''
    HEAD = "HEAD"
    '''(experimental) HTTP HEAD.

    :stability: experimental
    '''
    OPTIONS = "OPTIONS"
    '''(experimental) HTTP OPTIONS.

    :stability: experimental
    '''
    PATCH = "PATCH"
    '''(experimental) HTTP PATCH.

    :stability: experimental
    '''
    POST = "POST"
    '''(experimental) HTTP POST.

    :stability: experimental
    '''
    PUT = "PUT"
    '''(experimental) HTTP PUT.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.CorsPreflightOptions",
    jsii_struct_bases=[],
    name_mapping={
        "allow_credentials": "allowCredentials",
        "allow_headers": "allowHeaders",
        "allow_methods": "allowMethods",
        "allow_origins": "allowOrigins",
        "expose_headers": "exposeHeaders",
        "max_age": "maxAge",
    },
)
class CorsPreflightOptions:
    def __init__(
        self,
        *,
        allow_credentials: typing.Optional[builtins.bool] = None,
        allow_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        allow_methods: typing.Optional[typing.Sequence[CorsHttpMethod]] = None,
        allow_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
        expose_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Options for the CORS Configuration.

        :param allow_credentials: (experimental) Specifies whether credentials are included in the CORS request. Default: false
        :param allow_headers: (experimental) Represents a collection of allowed headers. Default: - No Headers are allowed.
        :param allow_methods: (experimental) Represents a collection of allowed HTTP methods. Default: - No Methods are allowed.
        :param allow_origins: (experimental) Represents a collection of allowed origins. Default: - No Origins are allowed.
        :param expose_headers: (experimental) Represents a collection of exposed headers. Default: - No Expose Headers are allowed.
        :param max_age: (experimental) The duration that the browser should cache preflight request results. Default: Duration.seconds(0)

        :stability: experimental
        :exampleMetadata: infused

        Example::

            apigwv2.HttpApi(self, "HttpProxyApi",
                cors_preflight=apigwv2.CorsPreflightOptions(
                    allow_headers=["Authorization"],
                    allow_methods=[apigwv2.CorsHttpMethod.GET, apigwv2.CorsHttpMethod.HEAD, apigwv2.CorsHttpMethod.OPTIONS, apigwv2.CorsHttpMethod.POST
                    ],
                    allow_origins=["*"],
                    max_age=Duration.days(10)
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8623074d52aadb0b4dc416f52273d5e1695739d7da72a818e4a16b0988313fa)
            check_type(argname="argument allow_credentials", value=allow_credentials, expected_type=type_hints["allow_credentials"])
            check_type(argname="argument allow_headers", value=allow_headers, expected_type=type_hints["allow_headers"])
            check_type(argname="argument allow_methods", value=allow_methods, expected_type=type_hints["allow_methods"])
            check_type(argname="argument allow_origins", value=allow_origins, expected_type=type_hints["allow_origins"])
            check_type(argname="argument expose_headers", value=expose_headers, expected_type=type_hints["expose_headers"])
            check_type(argname="argument max_age", value=max_age, expected_type=type_hints["max_age"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow_credentials is not None:
            self._values["allow_credentials"] = allow_credentials
        if allow_headers is not None:
            self._values["allow_headers"] = allow_headers
        if allow_methods is not None:
            self._values["allow_methods"] = allow_methods
        if allow_origins is not None:
            self._values["allow_origins"] = allow_origins
        if expose_headers is not None:
            self._values["expose_headers"] = expose_headers
        if max_age is not None:
            self._values["max_age"] = max_age

    @builtins.property
    def allow_credentials(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies whether credentials are included in the CORS request.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("allow_credentials")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Represents a collection of allowed headers.

        :default: - No Headers are allowed.

        :stability: experimental
        '''
        result = self._values.get("allow_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allow_methods(self) -> typing.Optional[typing.List[CorsHttpMethod]]:
        '''(experimental) Represents a collection of allowed HTTP methods.

        :default: - No Methods are allowed.

        :stability: experimental
        '''
        result = self._values.get("allow_methods")
        return typing.cast(typing.Optional[typing.List[CorsHttpMethod]], result)

    @builtins.property
    def allow_origins(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Represents a collection of allowed origins.

        :default: - No Origins are allowed.

        :stability: experimental
        '''
        result = self._values.get("allow_origins")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def expose_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Represents a collection of exposed headers.

        :default: - No Expose Headers are allowed.

        :stability: experimental
        '''
        result = self._values.get("expose_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_age(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The duration that the browser should cache preflight request results.

        :default: Duration.seconds(0)

        :stability: experimental
        '''
        result = self._values.get("max_age")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CorsPreflightOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.DomainMappingOptions",
    jsii_struct_bases=[],
    name_mapping={"domain_name": "domainName", "mapping_key": "mappingKey"},
)
class DomainMappingOptions:
    def __init__(
        self,
        *,
        domain_name: "IDomainName",
        mapping_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for DomainMapping.

        :param domain_name: (experimental) The domain name for the mapping.
        :param mapping_key: (experimental) The API mapping key. Leave it undefined for the root path mapping. Default: - empty key for the root path mapping

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
            
            # handler: lambda.Function
            # dn: apigwv2.DomainName
            
            
            api_demo = apigwv2.HttpApi(self, "DemoApi",
                default_integration=HttpLambdaIntegration("DefaultIntegration", handler),
                # https://${dn.domainName}/demo goes to apiDemo $default stage
                default_domain_mapping=apigwv2.DomainMappingOptions(
                    domain_name=dn,
                    mapping_key="demo"
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9c022929eefc93f95859e1c88a0b0f15538c5b557fbe539653100b894c61520)
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument mapping_key", value=mapping_key, expected_type=type_hints["mapping_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_name": domain_name,
        }
        if mapping_key is not None:
            self._values["mapping_key"] = mapping_key

    @builtins.property
    def domain_name(self) -> "IDomainName":
        '''(experimental) The domain name for the mapping.

        :stability: experimental
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast("IDomainName", result)

    @builtins.property
    def mapping_key(self) -> typing.Optional[builtins.str]:
        '''(experimental) The API mapping key.

        Leave it undefined for the root path mapping.

        :default: - empty key for the root path mapping

        :stability: experimental
        '''
        result = self._values.get("mapping_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainMappingOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.DomainNameAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "regional_domain_name": "regionalDomainName",
        "regional_hosted_zone_id": "regionalHostedZoneId",
    },
)
class DomainNameAttributes:
    def __init__(
        self,
        *,
        name: builtins.str,
        regional_domain_name: builtins.str,
        regional_hosted_zone_id: builtins.str,
    ) -> None:
        '''(experimental) custom domain name attributes.

        :param name: (experimental) domain name string.
        :param regional_domain_name: (experimental) The domain name associated with the regional endpoint for this custom domain name.
        :param regional_hosted_zone_id: (experimental) The region-specific Amazon Route 53 Hosted Zone ID of the regional endpoint.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            domain_name_attributes = apigatewayv2_alpha.DomainNameAttributes(
                name="name",
                regional_domain_name="regionalDomainName",
                regional_hosted_zone_id="regionalHostedZoneId"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3a28ea7d17c0cb32594b624176b2b5339560671719297d538c51a793079d6f8)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument regional_domain_name", value=regional_domain_name, expected_type=type_hints["regional_domain_name"])
            check_type(argname="argument regional_hosted_zone_id", value=regional_hosted_zone_id, expected_type=type_hints["regional_hosted_zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "regional_domain_name": regional_domain_name,
            "regional_hosted_zone_id": regional_hosted_zone_id,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) domain name string.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) The domain name associated with the regional endpoint for this custom domain name.

        :stability: experimental
        '''
        result = self._values.get("regional_domain_name")
        assert result is not None, "Required property 'regional_domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def regional_hosted_zone_id(self) -> builtins.str:
        '''(experimental) The region-specific Amazon Route 53 Hosted Zone ID of the regional endpoint.

        :stability: experimental
        '''
        result = self._values.get("regional_hosted_zone_id")
        assert result is not None, "Required property 'regional_hosted_zone_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainNameAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.EndpointOptions",
    jsii_struct_bases=[],
    name_mapping={
        "certificate": "certificate",
        "certificate_name": "certificateName",
        "endpoint_type": "endpointType",
        "ownership_certificate": "ownershipCertificate",
        "security_policy": "securityPolicy",
    },
)
class EndpointOptions:
    def __init__(
        self,
        *,
        certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
        certificate_name: typing.Optional[builtins.str] = None,
        endpoint_type: typing.Optional["EndpointType"] = None,
        ownership_certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        security_policy: typing.Optional["SecurityPolicy"] = None,
    ) -> None:
        '''(experimental) properties for creating a domain name endpoint.

        :param certificate: (experimental) The ACM certificate for this domain name. Certificate can be both ACM issued or imported.
        :param certificate_name: (experimental) The user-friendly name of the certificate that will be used by the endpoint for this domain name. Default: - No friendly certificate name
        :param endpoint_type: (experimental) The type of endpoint for this DomainName. Default: EndpointType.REGIONAL
        :param ownership_certificate: (experimental) A public certificate issued by ACM to validate that you own a custom domain. This parameter is required only when you configure mutual TLS authentication and you specify an ACM imported or private CA certificate for ``certificate``. The ownership certificate validates that you have permissions to use the domain name. Default: - only required when configuring mTLS
        :param security_policy: (experimental) The Transport Layer Security (TLS) version + cipher suite for this domain name. Default: SecurityPolicy.TLS_1_2

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            from aws_cdk import aws_certificatemanager as certificatemanager
            
            # certificate: certificatemanager.Certificate
            
            endpoint_options = apigatewayv2_alpha.EndpointOptions(
                certificate=certificate,
            
                # the properties below are optional
                certificate_name="certificateName",
                endpoint_type=apigatewayv2_alpha.EndpointType.EDGE,
                ownership_certificate=certificate,
                security_policy=apigatewayv2_alpha.SecurityPolicy.TLS_1_0
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a18b13421aac912723b2ab35f8a14b008971c520719c36b6764e8ff2bd43194)
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument certificate_name", value=certificate_name, expected_type=type_hints["certificate_name"])
            check_type(argname="argument endpoint_type", value=endpoint_type, expected_type=type_hints["endpoint_type"])
            check_type(argname="argument ownership_certificate", value=ownership_certificate, expected_type=type_hints["ownership_certificate"])
            check_type(argname="argument security_policy", value=security_policy, expected_type=type_hints["security_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificate": certificate,
        }
        if certificate_name is not None:
            self._values["certificate_name"] = certificate_name
        if endpoint_type is not None:
            self._values["endpoint_type"] = endpoint_type
        if ownership_certificate is not None:
            self._values["ownership_certificate"] = ownership_certificate
        if security_policy is not None:
            self._values["security_policy"] = security_policy

    @builtins.property
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''(experimental) The ACM certificate for this domain name.

        Certificate can be both ACM issued or imported.

        :stability: experimental
        '''
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, result)

    @builtins.property
    def certificate_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The user-friendly name of the certificate that will be used by the endpoint for this domain name.

        :default: - No friendly certificate name

        :stability: experimental
        '''
        result = self._values.get("certificate_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint_type(self) -> typing.Optional["EndpointType"]:
        '''(experimental) The type of endpoint for this DomainName.

        :default: EndpointType.REGIONAL

        :stability: experimental
        '''
        result = self._values.get("endpoint_type")
        return typing.cast(typing.Optional["EndpointType"], result)

    @builtins.property
    def ownership_certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''(experimental) A public certificate issued by ACM to validate that you own a custom domain.

        This parameter is required
        only when you configure mutual TLS authentication and you specify an ACM imported or private CA certificate
        for ``certificate``. The ownership certificate validates that you have permissions to use the domain name.

        :default: - only required when configuring mTLS

        :stability: experimental
        '''
        result = self._values.get("ownership_certificate")
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def security_policy(self) -> typing.Optional["SecurityPolicy"]:
        '''(experimental) The Transport Layer Security (TLS) version + cipher suite for this domain name.

        :default: SecurityPolicy.TLS_1_2

        :stability: experimental
        '''
        result = self._values.get("security_policy")
        return typing.cast(typing.Optional["SecurityPolicy"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EndpointOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.EndpointType")
class EndpointType(enum.Enum):
    '''(experimental) Endpoint type for a domain name.

    :stability: experimental
    '''

    EDGE = "EDGE"
    '''(experimental) For an edge-optimized custom domain name.

    :stability: experimental
    '''
    REGIONAL = "REGIONAL"
    '''(experimental) For a regional custom domain name.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.GrantInvokeOptions",
    jsii_struct_bases=[],
    name_mapping={"http_methods": "httpMethods"},
)
class GrantInvokeOptions:
    def __init__(
        self,
        *,
        http_methods: typing.Optional[typing.Sequence["HttpMethod"]] = None,
    ) -> None:
        '''(experimental) Options for granting invoke access.

        :param http_methods: (experimental) The HTTP methods to allow. Default: - the HttpMethod of the route

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            grant_invoke_options = apigatewayv2_alpha.GrantInvokeOptions(
                http_methods=[apigatewayv2_alpha.HttpMethod.ANY]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a82686daa9fd8d0f3123464a3edac12340e9f588999872022e157589c9935c8a)
            check_type(argname="argument http_methods", value=http_methods, expected_type=type_hints["http_methods"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if http_methods is not None:
            self._values["http_methods"] = http_methods

    @builtins.property
    def http_methods(self) -> typing.Optional[typing.List["HttpMethod"]]:
        '''(experimental) The HTTP methods to allow.

        :default: - the HttpMethod of the route

        :stability: experimental
        '''
        result = self._values.get("http_methods")
        return typing.cast(typing.Optional[typing.List["HttpMethod"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GrantInvokeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpApiAttributes",
    jsii_struct_bases=[],
    name_mapping={"http_api_id": "httpApiId", "api_endpoint": "apiEndpoint"},
)
class HttpApiAttributes:
    def __init__(
        self,
        *,
        http_api_id: builtins.str,
        api_endpoint: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Attributes for importing an HttpApi into the CDK.

        :param http_api_id: (experimental) The identifier of the HttpApi.
        :param api_endpoint: (experimental) The endpoint URL of the HttpApi. Default: - throws an error if apiEndpoint is accessed.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            http_api_attributes = apigatewayv2_alpha.HttpApiAttributes(
                http_api_id="httpApiId",
            
                # the properties below are optional
                api_endpoint="apiEndpoint"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca86693c779a127085f398e4f4b28effbcaffb7b0e4c3586085ba8720c18c3b6)
            check_type(argname="argument http_api_id", value=http_api_id, expected_type=type_hints["http_api_id"])
            check_type(argname="argument api_endpoint", value=api_endpoint, expected_type=type_hints["api_endpoint"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "http_api_id": http_api_id,
        }
        if api_endpoint is not None:
            self._values["api_endpoint"] = api_endpoint

    @builtins.property
    def http_api_id(self) -> builtins.str:
        '''(experimental) The identifier of the HttpApi.

        :stability: experimental
        '''
        result = self._values.get("http_api_id")
        assert result is not None, "Required property 'http_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_endpoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) The endpoint URL of the HttpApi.

        :default: - throws an error if apiEndpoint is accessed.

        :stability: experimental
        '''
        result = self._values.get("api_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpApiAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpApiProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_name": "apiName",
        "cors_preflight": "corsPreflight",
        "create_default_stage": "createDefaultStage",
        "default_authorization_scopes": "defaultAuthorizationScopes",
        "default_authorizer": "defaultAuthorizer",
        "default_domain_mapping": "defaultDomainMapping",
        "default_integration": "defaultIntegration",
        "description": "description",
        "disable_execute_api_endpoint": "disableExecuteApiEndpoint",
    },
)
class HttpApiProps:
    def __init__(
        self,
        *,
        api_name: typing.Optional[builtins.str] = None,
        cors_preflight: typing.Optional[typing.Union[CorsPreflightOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        create_default_stage: typing.Optional[builtins.bool] = None,
        default_authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_authorizer: typing.Optional["IHttpRouteAuthorizer"] = None,
        default_domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        default_integration: typing.Optional["HttpRouteIntegration"] = None,
        description: typing.Optional[builtins.str] = None,
        disable_execute_api_endpoint: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties to initialize an instance of ``HttpApi``.

        :param api_name: (experimental) Name for the HTTP API resource. Default: - id of the HttpApi construct.
        :param cors_preflight: (experimental) Specifies a CORS configuration for an API. Default: - CORS disabled.
        :param create_default_stage: (experimental) Whether a default stage and deployment should be automatically created. Default: true
        :param default_authorization_scopes: (experimental) Default OIDC scopes attached to all routes in the gateway, unless explicitly configured on the route. Default: - no default authorization scopes
        :param default_authorizer: (experimental) Default Authorizer to applied to all routes in the gateway. Default: - No authorizer
        :param default_domain_mapping: (experimental) Configure a custom domain with the API mapping resource to the HTTP API. Default: - no default domain mapping configured. meaningless if ``createDefaultStage`` is ``false``.
        :param default_integration: (experimental) An integration that will be configured on the catch-all route ($default). Default: - none
        :param description: (experimental) The description of the API. Default: - none
        :param disable_execute_api_endpoint: (experimental) Specifies whether clients can invoke your API using the default endpoint. By default, clients can invoke your API with the default ``https://{api_id}.execute-api.{region}.amazonaws.com`` endpoint. Enable this if you would like clients to use your custom domain name. Default: false execute-api endpoint enabled.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpAlbIntegration
            
            # lb: elbv2.ApplicationLoadBalancer
            
            listener = lb.add_listener("listener", port=80)
            listener.add_targets("target",
                port=80
            )
            
            http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
                default_integration=HttpAlbIntegration("DefaultIntegration", listener,
                    parameter_mapping=apigwv2.ParameterMapping().custom("myKey", "myValue")
                )
            )
        '''
        if isinstance(cors_preflight, dict):
            cors_preflight = CorsPreflightOptions(**cors_preflight)
        if isinstance(default_domain_mapping, dict):
            default_domain_mapping = DomainMappingOptions(**default_domain_mapping)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61f68792e068176f35bfd5b9b8d36c51601ad6882e6aa3ce1c951683b5d199d2)
            check_type(argname="argument api_name", value=api_name, expected_type=type_hints["api_name"])
            check_type(argname="argument cors_preflight", value=cors_preflight, expected_type=type_hints["cors_preflight"])
            check_type(argname="argument create_default_stage", value=create_default_stage, expected_type=type_hints["create_default_stage"])
            check_type(argname="argument default_authorization_scopes", value=default_authorization_scopes, expected_type=type_hints["default_authorization_scopes"])
            check_type(argname="argument default_authorizer", value=default_authorizer, expected_type=type_hints["default_authorizer"])
            check_type(argname="argument default_domain_mapping", value=default_domain_mapping, expected_type=type_hints["default_domain_mapping"])
            check_type(argname="argument default_integration", value=default_integration, expected_type=type_hints["default_integration"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_execute_api_endpoint", value=disable_execute_api_endpoint, expected_type=type_hints["disable_execute_api_endpoint"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if api_name is not None:
            self._values["api_name"] = api_name
        if cors_preflight is not None:
            self._values["cors_preflight"] = cors_preflight
        if create_default_stage is not None:
            self._values["create_default_stage"] = create_default_stage
        if default_authorization_scopes is not None:
            self._values["default_authorization_scopes"] = default_authorization_scopes
        if default_authorizer is not None:
            self._values["default_authorizer"] = default_authorizer
        if default_domain_mapping is not None:
            self._values["default_domain_mapping"] = default_domain_mapping
        if default_integration is not None:
            self._values["default_integration"] = default_integration
        if description is not None:
            self._values["description"] = description
        if disable_execute_api_endpoint is not None:
            self._values["disable_execute_api_endpoint"] = disable_execute_api_endpoint

    @builtins.property
    def api_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name for the HTTP API resource.

        :default: - id of the HttpApi construct.

        :stability: experimental
        '''
        result = self._values.get("api_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cors_preflight(self) -> typing.Optional[CorsPreflightOptions]:
        '''(experimental) Specifies a CORS configuration for an API.

        :default: - CORS disabled.

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-cors.html
        :stability: experimental
        '''
        result = self._values.get("cors_preflight")
        return typing.cast(typing.Optional[CorsPreflightOptions], result)

    @builtins.property
    def create_default_stage(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether a default stage and deployment should be automatically created.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("create_default_stage")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def default_authorization_scopes(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Default OIDC scopes attached to all routes in the gateway, unless explicitly configured on the route.

        :default: - no default authorization scopes

        :stability: experimental
        '''
        result = self._values.get("default_authorization_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_authorizer(self) -> typing.Optional["IHttpRouteAuthorizer"]:
        '''(experimental) Default Authorizer to applied to all routes in the gateway.

        :default: - No authorizer

        :stability: experimental
        '''
        result = self._values.get("default_authorizer")
        return typing.cast(typing.Optional["IHttpRouteAuthorizer"], result)

    @builtins.property
    def default_domain_mapping(self) -> typing.Optional[DomainMappingOptions]:
        '''(experimental) Configure a custom domain with the API mapping resource to the HTTP API.

        :default: - no default domain mapping configured. meaningless if ``createDefaultStage`` is ``false``.

        :stability: experimental
        '''
        result = self._values.get("default_domain_mapping")
        return typing.cast(typing.Optional[DomainMappingOptions], result)

    @builtins.property
    def default_integration(self) -> typing.Optional["HttpRouteIntegration"]:
        '''(experimental) An integration that will be configured on the catch-all route ($default).

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("default_integration")
        return typing.cast(typing.Optional["HttpRouteIntegration"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the API.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_execute_api_endpoint(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies whether clients can invoke your API using the default endpoint.

        By default, clients can invoke your API with the default
        ``https://{api_id}.execute-api.{region}.amazonaws.com`` endpoint. Enable
        this if you would like clients to use your custom domain name.

        :default: false execute-api endpoint enabled.

        :stability: experimental
        '''
        result = self._values.get("disable_execute_api_endpoint")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpAuthorizerAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_id": "authorizerId",
        "authorizer_type": "authorizerType",
    },
)
class HttpAuthorizerAttributes:
    def __init__(
        self,
        *,
        authorizer_id: builtins.str,
        authorizer_type: builtins.str,
    ) -> None:
        '''(experimental) Reference to an http authorizer.

        :param authorizer_id: (experimental) Id of the Authorizer.
        :param authorizer_type: (experimental) Type of authorizer. Possible values are: - JWT - JSON Web Token Authorizer - CUSTOM - Lambda Authorizer - NONE - No Authorization

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            http_authorizer_attributes = apigatewayv2_alpha.HttpAuthorizerAttributes(
                authorizer_id="authorizerId",
                authorizer_type="authorizerType"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e213cc5ff1a6a50f727adfa1a93746afabbb568dc170da0d58f5c5f6b4a65877)
            check_type(argname="argument authorizer_id", value=authorizer_id, expected_type=type_hints["authorizer_id"])
            check_type(argname="argument authorizer_type", value=authorizer_type, expected_type=type_hints["authorizer_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authorizer_id": authorizer_id,
            "authorizer_type": authorizer_type,
        }

    @builtins.property
    def authorizer_id(self) -> builtins.str:
        '''(experimental) Id of the Authorizer.

        :stability: experimental
        '''
        result = self._values.get("authorizer_id")
        assert result is not None, "Required property 'authorizer_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorizer_type(self) -> builtins.str:
        '''(experimental) Type of authorizer.

        Possible values are:

        - JWT - JSON Web Token Authorizer
        - CUSTOM - Lambda Authorizer
        - NONE - No Authorization

        :stability: experimental
        '''
        result = self._values.get("authorizer_type")
        assert result is not None, "Required property 'authorizer_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpAuthorizerAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "http_api": "httpApi",
        "identity_source": "identitySource",
        "type": "type",
        "authorizer_name": "authorizerName",
        "authorizer_uri": "authorizerUri",
        "enable_simple_responses": "enableSimpleResponses",
        "jwt_audience": "jwtAudience",
        "jwt_issuer": "jwtIssuer",
        "payload_format_version": "payloadFormatVersion",
        "results_cache_ttl": "resultsCacheTtl",
    },
)
class HttpAuthorizerProps:
    def __init__(
        self,
        *,
        http_api: "IHttpApi",
        identity_source: typing.Sequence[builtins.str],
        type: "HttpAuthorizerType",
        authorizer_name: typing.Optional[builtins.str] = None,
        authorizer_uri: typing.Optional[builtins.str] = None,
        enable_simple_responses: typing.Optional[builtins.bool] = None,
        jwt_audience: typing.Optional[typing.Sequence[builtins.str]] = None,
        jwt_issuer: typing.Optional[builtins.str] = None,
        payload_format_version: typing.Optional[AuthorizerPayloadVersion] = None,
        results_cache_ttl: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Properties to initialize an instance of ``HttpAuthorizer``.

        :param http_api: (experimental) HTTP Api to attach the authorizer to.
        :param identity_source: (experimental) The identity source for which authorization is requested.
        :param type: (experimental) The type of authorizer.
        :param authorizer_name: (experimental) Name of the authorizer. Default: - id of the HttpAuthorizer construct.
        :param authorizer_uri: (experimental) The authorizer's Uniform Resource Identifier (URI). For REQUEST authorizers, this must be a well-formed Lambda function URI. Default: - required for Request authorizer types
        :param enable_simple_responses: (experimental) Specifies whether a Lambda authorizer returns a response in a simple format. If enabled, the Lambda authorizer can return a boolean value instead of an IAM policy. Default: - The lambda authorizer must return an IAM policy as its response
        :param jwt_audience: (experimental) A list of the intended recipients of the JWT. A valid JWT must provide an aud that matches at least one entry in this list. Default: - required for JWT authorizer typess.
        :param jwt_issuer: (experimental) The base domain of the identity provider that issues JWT. Default: - required for JWT authorizer types.
        :param payload_format_version: (experimental) Specifies the format of the payload sent to an HTTP API Lambda authorizer. Default: AuthorizerPayloadVersion.VERSION_2_0 if the authorizer type is HttpAuthorizerType.LAMBDA
        :param results_cache_ttl: (experimental) How long APIGateway should cache the results. Max 1 hour. Default: - API Gateway will not cache authorizer responses

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            import aws_cdk as cdk
            
            # http_api: apigatewayv2_alpha.HttpApi
            
            http_authorizer_props = apigatewayv2_alpha.HttpAuthorizerProps(
                http_api=http_api,
                identity_source=["identitySource"],
                type=apigatewayv2_alpha.HttpAuthorizerType.IAM,
            
                # the properties below are optional
                authorizer_name="authorizerName",
                authorizer_uri="authorizerUri",
                enable_simple_responses=False,
                jwt_audience=["jwtAudience"],
                jwt_issuer="jwtIssuer",
                payload_format_version=apigatewayv2_alpha.AuthorizerPayloadVersion.VERSION_1_0,
                results_cache_ttl=cdk.Duration.minutes(30)
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__270c2096601be45fba89ecb508234f5870eaabd6d21813bc090ce9b1a459264d)
            check_type(argname="argument http_api", value=http_api, expected_type=type_hints["http_api"])
            check_type(argname="argument identity_source", value=identity_source, expected_type=type_hints["identity_source"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument authorizer_name", value=authorizer_name, expected_type=type_hints["authorizer_name"])
            check_type(argname="argument authorizer_uri", value=authorizer_uri, expected_type=type_hints["authorizer_uri"])
            check_type(argname="argument enable_simple_responses", value=enable_simple_responses, expected_type=type_hints["enable_simple_responses"])
            check_type(argname="argument jwt_audience", value=jwt_audience, expected_type=type_hints["jwt_audience"])
            check_type(argname="argument jwt_issuer", value=jwt_issuer, expected_type=type_hints["jwt_issuer"])
            check_type(argname="argument payload_format_version", value=payload_format_version, expected_type=type_hints["payload_format_version"])
            check_type(argname="argument results_cache_ttl", value=results_cache_ttl, expected_type=type_hints["results_cache_ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "http_api": http_api,
            "identity_source": identity_source,
            "type": type,
        }
        if authorizer_name is not None:
            self._values["authorizer_name"] = authorizer_name
        if authorizer_uri is not None:
            self._values["authorizer_uri"] = authorizer_uri
        if enable_simple_responses is not None:
            self._values["enable_simple_responses"] = enable_simple_responses
        if jwt_audience is not None:
            self._values["jwt_audience"] = jwt_audience
        if jwt_issuer is not None:
            self._values["jwt_issuer"] = jwt_issuer
        if payload_format_version is not None:
            self._values["payload_format_version"] = payload_format_version
        if results_cache_ttl is not None:
            self._values["results_cache_ttl"] = results_cache_ttl

    @builtins.property
    def http_api(self) -> "IHttpApi":
        '''(experimental) HTTP Api to attach the authorizer to.

        :stability: experimental
        '''
        result = self._values.get("http_api")
        assert result is not None, "Required property 'http_api' is missing"
        return typing.cast("IHttpApi", result)

    @builtins.property
    def identity_source(self) -> typing.List[builtins.str]:
        '''(experimental) The identity source for which authorization is requested.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-identitysource
        :stability: experimental
        '''
        result = self._values.get("identity_source")
        assert result is not None, "Required property 'identity_source' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def type(self) -> "HttpAuthorizerType":
        '''(experimental) The type of authorizer.

        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("HttpAuthorizerType", result)

    @builtins.property
    def authorizer_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the authorizer.

        :default: - id of the HttpAuthorizer construct.

        :stability: experimental
        '''
        result = self._values.get("authorizer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authorizer_uri(self) -> typing.Optional[builtins.str]:
        '''(experimental) The authorizer's Uniform Resource Identifier (URI).

        For REQUEST authorizers, this must be a well-formed Lambda function URI.

        :default: - required for Request authorizer types

        :stability: experimental
        '''
        result = self._values.get("authorizer_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_simple_responses(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies whether a Lambda authorizer returns a response in a simple format.

        If enabled, the Lambda authorizer can return a boolean value instead of an IAM policy.

        :default: - The lambda authorizer must return an IAM policy as its response

        :stability: experimental
        '''
        result = self._values.get("enable_simple_responses")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def jwt_audience(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of the intended recipients of the JWT.

        A valid JWT must provide an aud that matches at least one entry in this list.

        :default: - required for JWT authorizer typess.

        :stability: experimental
        '''
        result = self._values.get("jwt_audience")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jwt_issuer(self) -> typing.Optional[builtins.str]:
        '''(experimental) The base domain of the identity provider that issues JWT.

        :default: - required for JWT authorizer types.

        :stability: experimental
        '''
        result = self._values.get("jwt_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def payload_format_version(self) -> typing.Optional[AuthorizerPayloadVersion]:
        '''(experimental) Specifies the format of the payload sent to an HTTP API Lambda authorizer.

        :default: AuthorizerPayloadVersion.VERSION_2_0 if the authorizer type is HttpAuthorizerType.LAMBDA

        :stability: experimental
        '''
        result = self._values.get("payload_format_version")
        return typing.cast(typing.Optional[AuthorizerPayloadVersion], result)

    @builtins.property
    def results_cache_ttl(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) How long APIGateway should cache the results.

        Max 1 hour.

        :default: - API Gateway will not cache authorizer responses

        :stability: experimental
        '''
        result = self._values.get("results_cache_ttl")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpAuthorizerType")
class HttpAuthorizerType(enum.Enum):
    '''(experimental) Supported Authorizer types.

    :stability: experimental
    '''

    IAM = "IAM"
    '''(experimental) IAM Authorizer.

    :stability: experimental
    '''
    JWT = "JWT"
    '''(experimental) JSON Web Tokens.

    :stability: experimental
    '''
    LAMBDA = "LAMBDA"
    '''(experimental) Lambda Authorizer.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpConnectionType")
class HttpConnectionType(enum.Enum):
    '''(experimental) Supported connection types.

    :stability: experimental
    '''

    VPC_LINK = "VPC_LINK"
    '''(experimental) For private connections between API Gateway and resources in a VPC.

    :stability: experimental
    '''
    INTERNET = "INTERNET"
    '''(experimental) For connections through public routable internet.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpIntegrationProps",
    jsii_struct_bases=[],
    name_mapping={
        "http_api": "httpApi",
        "integration_type": "integrationType",
        "connection_id": "connectionId",
        "connection_type": "connectionType",
        "credentials": "credentials",
        "integration_subtype": "integrationSubtype",
        "integration_uri": "integrationUri",
        "method": "method",
        "parameter_mapping": "parameterMapping",
        "payload_format_version": "payloadFormatVersion",
        "secure_server_name": "secureServerName",
    },
)
class HttpIntegrationProps:
    def __init__(
        self,
        *,
        http_api: "IHttpApi",
        integration_type: "HttpIntegrationType",
        connection_id: typing.Optional[builtins.str] = None,
        connection_type: typing.Optional[HttpConnectionType] = None,
        credentials: typing.Optional["IntegrationCredentials"] = None,
        integration_subtype: typing.Optional["HttpIntegrationSubtype"] = None,
        integration_uri: typing.Optional[builtins.str] = None,
        method: typing.Optional["HttpMethod"] = None,
        parameter_mapping: typing.Optional["ParameterMapping"] = None,
        payload_format_version: typing.Optional["PayloadFormatVersion"] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) The integration properties.

        :param http_api: (experimental) The HTTP API to which this integration should be bound.
        :param integration_type: (experimental) Integration type.
        :param connection_id: (experimental) The ID of the VPC link for a private integration. Supported only for HTTP APIs. Default: - undefined
        :param connection_type: (experimental) The type of the network connection to the integration endpoint. Default: HttpConnectionType.INTERNET
        :param credentials: (experimental) The credentials with which to invoke the integration. Default: - no credentials, use resource-based permissions on supported AWS services
        :param integration_subtype: (experimental) Integration subtype. Used for AWS Service integrations, specifies the target of the integration. Default: - none, required if no ``integrationUri`` is defined.
        :param integration_uri: (experimental) Integration URI. This will be the function ARN in the case of ``HttpIntegrationType.AWS_PROXY``, or HTTP URL in the case of ``HttpIntegrationType.HTTP_PROXY``. Default: - none, required if no ``integrationSubtype`` is defined.
        :param method: (experimental) The HTTP method to use when calling the underlying HTTP proxy. Default: - none. required if the integration type is ``HttpIntegrationType.HTTP_PROXY``.
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param payload_format_version: (experimental) The version of the payload format. Default: - defaults to latest in the case of HttpIntegrationType.AWS_PROXY`, irrelevant otherwise.
        :param secure_server_name: (experimental) Specifies the TLS configuration for a private integration. Default: undefined private integration traffic will use HTTP protocol

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            # http_api: apigatewayv2_alpha.HttpApi
            # integration_credentials: apigatewayv2_alpha.IntegrationCredentials
            # parameter_mapping: apigatewayv2_alpha.ParameterMapping
            # payload_format_version: apigatewayv2_alpha.PayloadFormatVersion
            
            http_integration_props = apigatewayv2_alpha.HttpIntegrationProps(
                http_api=http_api,
                integration_type=apigatewayv2_alpha.HttpIntegrationType.HTTP_PROXY,
            
                # the properties below are optional
                connection_id="connectionId",
                connection_type=apigatewayv2_alpha.HttpConnectionType.VPC_LINK,
                credentials=integration_credentials,
                integration_subtype=apigatewayv2_alpha.HttpIntegrationSubtype.EVENTBRIDGE_PUT_EVENTS,
                integration_uri="integrationUri",
                method=apigatewayv2_alpha.HttpMethod.ANY,
                parameter_mapping=parameter_mapping,
                payload_format_version=payload_format_version,
                secure_server_name="secureServerName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e70b5fc9ef16c84251eedf90fb9f4578a5231e285c86d485055a9875610b863)
            check_type(argname="argument http_api", value=http_api, expected_type=type_hints["http_api"])
            check_type(argname="argument integration_type", value=integration_type, expected_type=type_hints["integration_type"])
            check_type(argname="argument connection_id", value=connection_id, expected_type=type_hints["connection_id"])
            check_type(argname="argument connection_type", value=connection_type, expected_type=type_hints["connection_type"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument integration_subtype", value=integration_subtype, expected_type=type_hints["integration_subtype"])
            check_type(argname="argument integration_uri", value=integration_uri, expected_type=type_hints["integration_uri"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument parameter_mapping", value=parameter_mapping, expected_type=type_hints["parameter_mapping"])
            check_type(argname="argument payload_format_version", value=payload_format_version, expected_type=type_hints["payload_format_version"])
            check_type(argname="argument secure_server_name", value=secure_server_name, expected_type=type_hints["secure_server_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "http_api": http_api,
            "integration_type": integration_type,
        }
        if connection_id is not None:
            self._values["connection_id"] = connection_id
        if connection_type is not None:
            self._values["connection_type"] = connection_type
        if credentials is not None:
            self._values["credentials"] = credentials
        if integration_subtype is not None:
            self._values["integration_subtype"] = integration_subtype
        if integration_uri is not None:
            self._values["integration_uri"] = integration_uri
        if method is not None:
            self._values["method"] = method
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if payload_format_version is not None:
            self._values["payload_format_version"] = payload_format_version
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name

    @builtins.property
    def http_api(self) -> "IHttpApi":
        '''(experimental) The HTTP API to which this integration should be bound.

        :stability: experimental
        '''
        result = self._values.get("http_api")
        assert result is not None, "Required property 'http_api' is missing"
        return typing.cast("IHttpApi", result)

    @builtins.property
    def integration_type(self) -> "HttpIntegrationType":
        '''(experimental) Integration type.

        :stability: experimental
        '''
        result = self._values.get("integration_type")
        assert result is not None, "Required property 'integration_type' is missing"
        return typing.cast("HttpIntegrationType", result)

    @builtins.property
    def connection_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ID of the VPC link for a private integration.

        Supported only for HTTP APIs.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("connection_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_type(self) -> typing.Optional[HttpConnectionType]:
        '''(experimental) The type of the network connection to the integration endpoint.

        :default: HttpConnectionType.INTERNET

        :stability: experimental
        '''
        result = self._values.get("connection_type")
        return typing.cast(typing.Optional[HttpConnectionType], result)

    @builtins.property
    def credentials(self) -> typing.Optional["IntegrationCredentials"]:
        '''(experimental) The credentials with which to invoke the integration.

        :default: - no credentials, use resource-based permissions on supported AWS services

        :stability: experimental
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional["IntegrationCredentials"], result)

    @builtins.property
    def integration_subtype(self) -> typing.Optional["HttpIntegrationSubtype"]:
        '''(experimental) Integration subtype.

        Used for AWS Service integrations, specifies the target of the integration.

        :default: - none, required if no ``integrationUri`` is defined.

        :stability: experimental
        '''
        result = self._values.get("integration_subtype")
        return typing.cast(typing.Optional["HttpIntegrationSubtype"], result)

    @builtins.property
    def integration_uri(self) -> typing.Optional[builtins.str]:
        '''(experimental) Integration URI.

        This will be the function ARN in the case of ``HttpIntegrationType.AWS_PROXY``,
        or HTTP URL in the case of ``HttpIntegrationType.HTTP_PROXY``.

        :default: - none, required if no ``integrationSubtype`` is defined.

        :stability: experimental
        '''
        result = self._values.get("integration_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def method(self) -> typing.Optional["HttpMethod"]:
        '''(experimental) The HTTP method to use when calling the underlying HTTP proxy.

        :default: - none. required if the integration type is ``HttpIntegrationType.HTTP_PROXY``.

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional["HttpMethod"], result)

    @builtins.property
    def parameter_mapping(self) -> typing.Optional["ParameterMapping"]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional["ParameterMapping"], result)

    @builtins.property
    def payload_format_version(self) -> typing.Optional["PayloadFormatVersion"]:
        '''(experimental) The version of the payload format.

        :default: - defaults to latest in the case of HttpIntegrationType.AWS_PROXY`, irrelevant otherwise.

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
        :stability: experimental
        '''
        result = self._values.get("payload_format_version")
        return typing.cast(typing.Optional["PayloadFormatVersion"], result)

    @builtins.property
    def secure_server_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specifies the TLS configuration for a private integration.

        :default: undefined private integration traffic will use HTTP protocol

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-tlsconfig.html
        :stability: experimental
        '''
        result = self._values.get("secure_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpIntegrationSubtype")
class HttpIntegrationSubtype(enum.Enum):
    '''(experimental) Supported integration subtypes.

    :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-aws-services-reference.html
    :stability: experimental
    '''

    EVENTBRIDGE_PUT_EVENTS = "EVENTBRIDGE_PUT_EVENTS"
    '''(experimental) EventBridge PutEvents integration.

    :stability: experimental
    '''
    SQS_SEND_MESSAGE = "SQS_SEND_MESSAGE"
    '''(experimental) SQS SendMessage integration.

    :stability: experimental
    '''
    SQS_RECEIVE_MESSAGE = "SQS_RECEIVE_MESSAGE"
    '''(experimental) SQS ReceiveMessage integration,.

    :stability: experimental
    '''
    SQS_DELETE_MESSAGE = "SQS_DELETE_MESSAGE"
    '''(experimental) SQS DeleteMessage integration,.

    :stability: experimental
    '''
    SQS_PURGE_QUEUE = "SQS_PURGE_QUEUE"
    '''(experimental) SQS PurgeQueue integration.

    :stability: experimental
    '''
    APPCONFIG_GET_CONFIGURATION = "APPCONFIG_GET_CONFIGURATION"
    '''(experimental) AppConfig GetConfiguration integration.

    :stability: experimental
    '''
    KINESIS_PUT_RECORD = "KINESIS_PUT_RECORD"
    '''(experimental) Kinesis PutRecord integration.

    :stability: experimental
    '''
    STEPFUNCTIONS_START_EXECUTION = "STEPFUNCTIONS_START_EXECUTION"
    '''(experimental) Step Functions StartExecution integration.

    :stability: experimental
    '''
    STEPFUNCTIONS_START_SYNC_EXECUTION = "STEPFUNCTIONS_START_SYNC_EXECUTION"
    '''(experimental) Step Functions StartSyncExecution integration.

    :stability: experimental
    '''
    STEPFUNCTIONS_STOP_EXECUTION = "STEPFUNCTIONS_STOP_EXECUTION"
    '''(experimental) Step Functions StopExecution integration.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpIntegrationType")
class HttpIntegrationType(enum.Enum):
    '''(experimental) Supported integration types.

    :stability: experimental
    '''

    HTTP_PROXY = "HTTP_PROXY"
    '''(experimental) Integration type is an HTTP proxy.

    For integrating the route or method request with an HTTP endpoint, with the
    client request passed through as-is. This is also referred to as HTTP proxy
    integration. For HTTP API private integrations, use an HTTP_PROXY integration.

    :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-http.html
    :stability: experimental
    '''
    AWS_PROXY = "AWS_PROXY"
    '''(experimental) Integration type is an AWS proxy.

    For integrating the route or method request with a Lambda function or other
    AWS service action. This integration is also referred to as a Lambda proxy
    integration.

    :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpMethod")
class HttpMethod(enum.Enum):
    '''(experimental) Supported HTTP methods.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration, HttpLambdaIntegration
        
        # books_default_fn: lambda.Function
        
        
        get_books_integration = HttpUrlIntegration("GetBooksIntegration", "https://get-books-proxy.example.com")
        books_default_integration = HttpLambdaIntegration("BooksIntegration", books_default_fn)
        
        http_api = apigwv2.HttpApi(self, "HttpApi")
        
        http_api.add_routes(
            path="/books",
            methods=[apigwv2.HttpMethod.GET],
            integration=get_books_integration
        )
        http_api.add_routes(
            path="/books",
            methods=[apigwv2.HttpMethod.ANY],
            integration=books_default_integration
        )
    '''

    ANY = "ANY"
    '''(experimental) HTTP ANY.

    :stability: experimental
    '''
    DELETE = "DELETE"
    '''(experimental) HTTP DELETE.

    :stability: experimental
    '''
    GET = "GET"
    '''(experimental) HTTP GET.

    :stability: experimental
    '''
    HEAD = "HEAD"
    '''(experimental) HTTP HEAD.

    :stability: experimental
    '''
    OPTIONS = "OPTIONS"
    '''(experimental) HTTP OPTIONS.

    :stability: experimental
    '''
    PATCH = "PATCH"
    '''(experimental) HTTP PATCH.

    :stability: experimental
    '''
    POST = "POST"
    '''(experimental) HTTP POST.

    :stability: experimental
    '''
    PUT = "PUT"
    '''(experimental) HTTP PUT.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpRouteAuthorizerBindOptions",
    jsii_struct_bases=[],
    name_mapping={"route": "route", "scope": "scope"},
)
class HttpRouteAuthorizerBindOptions:
    def __init__(
        self,
        *,
        route: "IHttpRoute",
        scope: _constructs_77d1e7e8.Construct,
    ) -> None:
        '''(experimental) Input to the bind() operation, that binds an authorizer to a route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            import constructs as constructs
            
            # construct: constructs.Construct
            # http_route: apigatewayv2_alpha.HttpRoute
            
            http_route_authorizer_bind_options = apigatewayv2_alpha.HttpRouteAuthorizerBindOptions(
                route=http_route,
                scope=construct
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__327eab42c70e54708c05239cc92e1d413d8f439a24b6448c6de2d0f2d4df7521)
            check_type(argname="argument route", value=route, expected_type=type_hints["route"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "route": route,
            "scope": scope,
        }

    @builtins.property
    def route(self) -> "IHttpRoute":
        '''(experimental) The route to which the authorizer is being bound.

        :stability: experimental
        '''
        result = self._values.get("route")
        assert result is not None, "Required property 'route' is missing"
        return typing.cast("IHttpRoute", result)

    @builtins.property
    def scope(self) -> _constructs_77d1e7e8.Construct:
        '''(experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(_constructs_77d1e7e8.Construct, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpRouteAuthorizerBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpRouteAuthorizerConfig",
    jsii_struct_bases=[],
    name_mapping={
        "authorization_type": "authorizationType",
        "authorization_scopes": "authorizationScopes",
        "authorizer_id": "authorizerId",
    },
)
class HttpRouteAuthorizerConfig:
    def __init__(
        self,
        *,
        authorization_type: builtins.str,
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        authorizer_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Results of binding an authorizer to an http route.

        :param authorization_type: (experimental) The type of authorization. Possible values are: - AWS_IAM - IAM Authorizer - JWT - JSON Web Token Authorizer - CUSTOM - Lambda Authorizer - NONE - No Authorization
        :param authorization_scopes: (experimental) The list of OIDC scopes to include in the authorization. Default: - no authorization scopes
        :param authorizer_id: (experimental) The authorizer id. Default: - No authorizer id (useful for AWS_IAM route authorizer)

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            http_route_authorizer_config = apigatewayv2_alpha.HttpRouteAuthorizerConfig(
                authorization_type="authorizationType",
            
                # the properties below are optional
                authorization_scopes=["authorizationScopes"],
                authorizer_id="authorizerId"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23fa1130cc8cec3f96c4c7be76f4fde0189dfa2fd6410ede8be1c8e24a88a0f2)
            check_type(argname="argument authorization_type", value=authorization_type, expected_type=type_hints["authorization_type"])
            check_type(argname="argument authorization_scopes", value=authorization_scopes, expected_type=type_hints["authorization_scopes"])
            check_type(argname="argument authorizer_id", value=authorizer_id, expected_type=type_hints["authorizer_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authorization_type": authorization_type,
        }
        if authorization_scopes is not None:
            self._values["authorization_scopes"] = authorization_scopes
        if authorizer_id is not None:
            self._values["authorizer_id"] = authorizer_id

    @builtins.property
    def authorization_type(self) -> builtins.str:
        '''(experimental) The type of authorization.

        Possible values are:

        - AWS_IAM - IAM Authorizer
        - JWT - JSON Web Token Authorizer
        - CUSTOM - Lambda Authorizer
        - NONE - No Authorization

        :stability: experimental
        '''
        result = self._values.get("authorization_type")
        assert result is not None, "Required property 'authorization_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorization_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The list of OIDC scopes to include in the authorization.

        :default: - no authorization scopes

        :stability: experimental
        '''
        result = self._values.get("authorization_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def authorizer_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The authorizer id.

        :default: - No authorizer id (useful for AWS_IAM route authorizer)

        :stability: experimental
        '''
        result = self._values.get("authorizer_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpRouteAuthorizerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HttpRouteIntegration(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpRouteIntegration",
):
    '''(experimental) The interface that various route integration classes will inherit.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpAlbIntegration
        
        # lb: elbv2.ApplicationLoadBalancer
        
        listener = lb.add_listener("listener", port=80)
        listener.add_targets("target",
            port=80
        )
        
        http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
            default_integration=HttpAlbIntegration("DefaultIntegration", listener,
                parameter_mapping=apigwv2.ParameterMapping().custom("myKey", "myValue")
            )
        )
    '''

    def __init__(self, id: builtins.str) -> None:
        '''(experimental) Initialize an integration for a route on http api.

        :param id: id of the underlying ``HttpIntegration`` construct.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d2d16b160325ee41bba7780d2678d810d12da5f663f886f5c8a810a06c66fef)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [id])

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def bind(
        self,
        *,
        route: "IHttpRoute",
        scope: _constructs_77d1e7e8.Construct,
    ) -> "HttpRouteIntegrationConfig":
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="completeBind")
    def _complete_bind(
        self,
        *,
        route: "IHttpRoute",
        scope: _constructs_77d1e7e8.Construct,
    ) -> None:
        '''(experimental) Complete the binding of the integration to the route.

        In some cases, there is
        some additional work to do, such as adding permissions for the API to access
        the target. This work is necessary whether the integration has just been
        created for this route or it is an existing one, previously created for other
        routes. In most cases, however, concrete implementations do not need to
        override this method.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        _options = HttpRouteIntegrationBindOptions(route=route, scope=scope)

        return typing.cast(None, jsii.invoke(self, "completeBind", [_options]))


class _HttpRouteIntegrationProxy(HttpRouteIntegration):
    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: "IHttpRoute",
        scope: _constructs_77d1e7e8.Construct,
    ) -> "HttpRouteIntegrationConfig":
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = HttpRouteIntegrationBindOptions(route=route, scope=scope)

        return typing.cast("HttpRouteIntegrationConfig", jsii.invoke(self, "bind", [options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, HttpRouteIntegration).__jsii_proxy_class__ = lambda : _HttpRouteIntegrationProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpRouteIntegrationBindOptions",
    jsii_struct_bases=[],
    name_mapping={"route": "route", "scope": "scope"},
)
class HttpRouteIntegrationBindOptions:
    def __init__(
        self,
        *,
        route: "IHttpRoute",
        scope: _constructs_77d1e7e8.Construct,
    ) -> None:
        '''(experimental) Options to the HttpRouteIntegration during its bind operation.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            import constructs as constructs
            
            # construct: constructs.Construct
            # http_route: apigatewayv2_alpha.HttpRoute
            
            http_route_integration_bind_options = apigatewayv2_alpha.HttpRouteIntegrationBindOptions(
                route=http_route,
                scope=construct
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fee001518b0d0335530b5174be6d0d04745ad94a5bffe05a6d9007712a52eb52)
            check_type(argname="argument route", value=route, expected_type=type_hints["route"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "route": route,
            "scope": scope,
        }

    @builtins.property
    def route(self) -> "IHttpRoute":
        '''(experimental) The route to which this is being bound.

        :stability: experimental
        '''
        result = self._values.get("route")
        assert result is not None, "Required property 'route' is missing"
        return typing.cast("IHttpRoute", result)

    @builtins.property
    def scope(self) -> _constructs_77d1e7e8.Construct:
        '''(experimental) The current scope in which the bind is occurring.

        If the ``HttpRouteIntegration`` being bound creates additional constructs,
        this will be used as their parent scope.

        :stability: experimental
        '''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(_constructs_77d1e7e8.Construct, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpRouteIntegrationBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpRouteIntegrationConfig",
    jsii_struct_bases=[],
    name_mapping={
        "payload_format_version": "payloadFormatVersion",
        "type": "type",
        "connection_id": "connectionId",
        "connection_type": "connectionType",
        "credentials": "credentials",
        "method": "method",
        "parameter_mapping": "parameterMapping",
        "secure_server_name": "secureServerName",
        "subtype": "subtype",
        "uri": "uri",
    },
)
class HttpRouteIntegrationConfig:
    def __init__(
        self,
        *,
        payload_format_version: "PayloadFormatVersion",
        type: HttpIntegrationType,
        connection_id: typing.Optional[builtins.str] = None,
        connection_type: typing.Optional[HttpConnectionType] = None,
        credentials: typing.Optional["IntegrationCredentials"] = None,
        method: typing.Optional[HttpMethod] = None,
        parameter_mapping: typing.Optional["ParameterMapping"] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        subtype: typing.Optional[HttpIntegrationSubtype] = None,
        uri: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Config returned back as a result of the bind.

        :param payload_format_version: (experimental) Payload format version in the case of lambda proxy integration. Default: - undefined
        :param type: (experimental) Integration type.
        :param connection_id: (experimental) The ID of the VPC link for a private integration. Supported only for HTTP APIs. Default: - undefined
        :param connection_type: (experimental) The type of the network connection to the integration endpoint. Default: HttpConnectionType.INTERNET
        :param credentials: (experimental) The credentials with which to invoke the integration. Default: - no credentials, use resource-based permissions on supported AWS services
        :param method: (experimental) The HTTP method that must be used to invoke the underlying proxy. Required for ``HttpIntegrationType.HTTP_PROXY`` Default: - undefined
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param subtype: (experimental) Integration subtype. Default: - none, required if no ``integrationUri`` is defined.
        :param uri: (experimental) Integration URI. Default: - none, required if no ``integrationSubtype`` is defined.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            # integration_credentials: apigatewayv2_alpha.IntegrationCredentials
            # parameter_mapping: apigatewayv2_alpha.ParameterMapping
            # payload_format_version: apigatewayv2_alpha.PayloadFormatVersion
            
            http_route_integration_config = apigatewayv2_alpha.HttpRouteIntegrationConfig(
                payload_format_version=payload_format_version,
                type=apigatewayv2_alpha.HttpIntegrationType.HTTP_PROXY,
            
                # the properties below are optional
                connection_id="connectionId",
                connection_type=apigatewayv2_alpha.HttpConnectionType.VPC_LINK,
                credentials=integration_credentials,
                method=apigatewayv2_alpha.HttpMethod.ANY,
                parameter_mapping=parameter_mapping,
                secure_server_name="secureServerName",
                subtype=apigatewayv2_alpha.HttpIntegrationSubtype.EVENTBRIDGE_PUT_EVENTS,
                uri="uri"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d07656a3841a48dd4643d0e10742dee8735d4fa1b6dec4e77afe67a3c12f2dd)
            check_type(argname="argument payload_format_version", value=payload_format_version, expected_type=type_hints["payload_format_version"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument connection_id", value=connection_id, expected_type=type_hints["connection_id"])
            check_type(argname="argument connection_type", value=connection_type, expected_type=type_hints["connection_type"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument parameter_mapping", value=parameter_mapping, expected_type=type_hints["parameter_mapping"])
            check_type(argname="argument secure_server_name", value=secure_server_name, expected_type=type_hints["secure_server_name"])
            check_type(argname="argument subtype", value=subtype, expected_type=type_hints["subtype"])
            check_type(argname="argument uri", value=uri, expected_type=type_hints["uri"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "payload_format_version": payload_format_version,
            "type": type,
        }
        if connection_id is not None:
            self._values["connection_id"] = connection_id
        if connection_type is not None:
            self._values["connection_type"] = connection_type
        if credentials is not None:
            self._values["credentials"] = credentials
        if method is not None:
            self._values["method"] = method
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if subtype is not None:
            self._values["subtype"] = subtype
        if uri is not None:
            self._values["uri"] = uri

    @builtins.property
    def payload_format_version(self) -> "PayloadFormatVersion":
        '''(experimental) Payload format version in the case of lambda proxy integration.

        :default: - undefined

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
        :stability: experimental
        '''
        result = self._values.get("payload_format_version")
        assert result is not None, "Required property 'payload_format_version' is missing"
        return typing.cast("PayloadFormatVersion", result)

    @builtins.property
    def type(self) -> HttpIntegrationType:
        '''(experimental) Integration type.

        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(HttpIntegrationType, result)

    @builtins.property
    def connection_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ID of the VPC link for a private integration.

        Supported only for HTTP APIs.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("connection_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_type(self) -> typing.Optional[HttpConnectionType]:
        '''(experimental) The type of the network connection to the integration endpoint.

        :default: HttpConnectionType.INTERNET

        :stability: experimental
        '''
        result = self._values.get("connection_type")
        return typing.cast(typing.Optional[HttpConnectionType], result)

    @builtins.property
    def credentials(self) -> typing.Optional["IntegrationCredentials"]:
        '''(experimental) The credentials with which to invoke the integration.

        :default: - no credentials, use resource-based permissions on supported AWS services

        :stability: experimental
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional["IntegrationCredentials"], result)

    @builtins.property
    def method(self) -> typing.Optional[HttpMethod]:
        '''(experimental) The HTTP method that must be used to invoke the underlying proxy.

        Required for ``HttpIntegrationType.HTTP_PROXY``

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[HttpMethod], result)

    @builtins.property
    def parameter_mapping(self) -> typing.Optional["ParameterMapping"]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional["ParameterMapping"], result)

    @builtins.property
    def secure_server_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specifies the server name to verified by HTTPS when calling the backend integration.

        :default: undefined private integration traffic will use HTTP protocol

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-tlsconfig.html
        :stability: experimental
        '''
        result = self._values.get("secure_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subtype(self) -> typing.Optional[HttpIntegrationSubtype]:
        '''(experimental) Integration subtype.

        :default: - none, required if no ``integrationUri`` is defined.

        :stability: experimental
        '''
        result = self._values.get("subtype")
        return typing.cast(typing.Optional[HttpIntegrationSubtype], result)

    @builtins.property
    def uri(self) -> typing.Optional[builtins.str]:
        '''(experimental) Integration URI.

        :default: - none, required if no ``integrationSubtype`` is defined.

        :stability: experimental
        '''
        result = self._values.get("uri")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpRouteIntegrationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HttpRouteKey(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpRouteKey",
):
    '''(experimental) HTTP route in APIGateway is a combination of the HTTP method and the path component.

    This class models that combination.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
        
        http_route_key = apigatewayv2_alpha.HttpRouteKey.with("path", apigatewayv2_alpha.HttpMethod.ANY)
    '''

    @jsii.member(jsii_name="with")
    @builtins.classmethod
    def with_(
        cls,
        path: builtins.str,
        method: typing.Optional[HttpMethod] = None,
    ) -> "HttpRouteKey":
        '''(experimental) Create a route key with the combination of the path and the method.

        :param path: -
        :param method: default is 'ANY'.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__757949aa83516e4dc3de82eaf70c9ec58058087715b274d9a080b33530b01213)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
        return typing.cast("HttpRouteKey", jsii.sinvoke(cls, "with", [path, method]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT")
    def DEFAULT(cls) -> "HttpRouteKey":
        '''(experimental) The catch-all route of the API, i.e., when no other routes match.

        :stability: experimental
        '''
        return typing.cast("HttpRouteKey", jsii.sget(cls, "DEFAULT"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        '''(experimental) The key to the RouteKey as recognized by APIGateway.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> HttpMethod:
        '''(experimental) The method of the route.

        :stability: experimental
        '''
        return typing.cast(HttpMethod, jsii.get(self, "method"))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> typing.Optional[builtins.str]:
        '''(experimental) The path part of this RouteKey.

        Returns ``undefined`` when ``RouteKey.DEFAULT`` is used.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "path"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpRouteProps",
    jsii_struct_bases=[BatchHttpRouteOptions],
    name_mapping={
        "integration": "integration",
        "http_api": "httpApi",
        "route_key": "routeKey",
        "authorization_scopes": "authorizationScopes",
        "authorizer": "authorizer",
    },
)
class HttpRouteProps(BatchHttpRouteOptions):
    def __init__(
        self,
        *,
        integration: HttpRouteIntegration,
        http_api: "IHttpApi",
        route_key: HttpRouteKey,
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        authorizer: typing.Optional["IHttpRouteAuthorizer"] = None,
    ) -> None:
        '''(experimental) Properties to initialize a new Route.

        :param integration: (experimental) The integration to be configured on this route.
        :param http_api: (experimental) the API the route is associated with.
        :param route_key: (experimental) The key to this route. This is a combination of an HTTP method and an HTTP path.
        :param authorization_scopes: (experimental) The list of OIDC scopes to include in the authorization. These scopes will be merged with the scopes from the attached authorizer Default: - no additional authorization scopes
        :param authorizer: (experimental) Authorizer for a WebSocket API or an HTTP API. Default: - No authorizer

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            # http_api: apigatewayv2_alpha.HttpApi
            # http_route_authorizer: apigatewayv2_alpha.IHttpRouteAuthorizer
            # http_route_integration: apigatewayv2_alpha.HttpRouteIntegration
            # http_route_key: apigatewayv2_alpha.HttpRouteKey
            
            http_route_props = apigatewayv2_alpha.HttpRouteProps(
                http_api=http_api,
                integration=http_route_integration,
                route_key=http_route_key,
            
                # the properties below are optional
                authorization_scopes=["authorizationScopes"],
                authorizer=http_route_authorizer
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a43a4a903025b4c98824c40d09ba7a3ec865a0a5902fb4f311846b446c460133)
            check_type(argname="argument integration", value=integration, expected_type=type_hints["integration"])
            check_type(argname="argument http_api", value=http_api, expected_type=type_hints["http_api"])
            check_type(argname="argument route_key", value=route_key, expected_type=type_hints["route_key"])
            check_type(argname="argument authorization_scopes", value=authorization_scopes, expected_type=type_hints["authorization_scopes"])
            check_type(argname="argument authorizer", value=authorizer, expected_type=type_hints["authorizer"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration": integration,
            "http_api": http_api,
            "route_key": route_key,
        }
        if authorization_scopes is not None:
            self._values["authorization_scopes"] = authorization_scopes
        if authorizer is not None:
            self._values["authorizer"] = authorizer

    @builtins.property
    def integration(self) -> HttpRouteIntegration:
        '''(experimental) The integration to be configured on this route.

        :stability: experimental
        '''
        result = self._values.get("integration")
        assert result is not None, "Required property 'integration' is missing"
        return typing.cast(HttpRouteIntegration, result)

    @builtins.property
    def http_api(self) -> "IHttpApi":
        '''(experimental) the API the route is associated with.

        :stability: experimental
        '''
        result = self._values.get("http_api")
        assert result is not None, "Required property 'http_api' is missing"
        return typing.cast("IHttpApi", result)

    @builtins.property
    def route_key(self) -> HttpRouteKey:
        '''(experimental) The key to this route.

        This is a combination of an HTTP method and an HTTP path.

        :stability: experimental
        '''
        result = self._values.get("route_key")
        assert result is not None, "Required property 'route_key' is missing"
        return typing.cast(HttpRouteKey, result)

    @builtins.property
    def authorization_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The list of OIDC scopes to include in the authorization.

        These scopes will be merged with the scopes from the attached authorizer

        :default: - no additional authorization scopes

        :stability: experimental
        '''
        result = self._values.get("authorization_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def authorizer(self) -> typing.Optional["IHttpRouteAuthorizer"]:
        '''(experimental) Authorizer for a WebSocket API or an HTTP API.

        :default: - No authorizer

        :stability: experimental
        '''
        result = self._values.get("authorizer")
        return typing.cast(typing.Optional["IHttpRouteAuthorizer"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpRouteProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IApi")
class IApi(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents a API Gateway HTTP/WebSocket API.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="apiEndpoint")
    def api_endpoint(self) -> builtins.str:
        '''(experimental) The default endpoint for an API.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''(experimental) The identifier of this API Gateway API.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this Api Gateway.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - average over 5 minutes

        :stability: experimental
        '''
        ...


class _IApiProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents a API Gateway HTTP/WebSocket API.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IApi"

    @builtins.property
    @jsii.member(jsii_name="apiEndpoint")
    def api_endpoint(self) -> builtins.str:
        '''(experimental) The default endpoint for an API.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''(experimental) The identifier of this API Gateway API.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this Api Gateway.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - average over 5 minutes

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c475fcfbd8ec2d43f9f067afa8d49c21d334d5c85f25834be833f0c107d99e8e)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IApi).__jsii_proxy_class__ = lambda : _IApiProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IApiMapping")
class IApiMapping(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an ApiGatewayV2 ApiMapping resource.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="apiMappingId")
    def api_mapping_id(self) -> builtins.str:
        '''(experimental) ID of the api mapping.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IApiMappingProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents an ApiGatewayV2 ApiMapping resource.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IApiMapping"

    @builtins.property
    @jsii.member(jsii_name="apiMappingId")
    def api_mapping_id(self) -> builtins.str:
        '''(experimental) ID of the api mapping.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiMappingId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IApiMapping).__jsii_proxy_class__ = lambda : _IApiMappingProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IAuthorizer")
class IAuthorizer(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an Authorizer.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="authorizerId")
    def authorizer_id(self) -> builtins.str:
        '''(experimental) Id of the Authorizer.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IAuthorizerProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents an Authorizer.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IAuthorizer"

    @builtins.property
    @jsii.member(jsii_name="authorizerId")
    def authorizer_id(self) -> builtins.str:
        '''(experimental) Id of the Authorizer.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "authorizerId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAuthorizer).__jsii_proxy_class__ = lambda : _IAuthorizerProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IDomainName")
class IDomainName(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an APIGatewayV2 DomainName.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The custom domain name.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) The domain name associated with the regional endpoint for this custom domain name.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="regionalHostedZoneId")
    def regional_hosted_zone_id(self) -> builtins.str:
        '''(experimental) The region-specific Amazon Route 53 Hosted Zone ID of the regional endpoint.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IDomainNameProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents an APIGatewayV2 DomainName.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IDomainName"

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The custom domain name.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) The domain name associated with the regional endpoint for this custom domain name.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "regionalDomainName"))

    @builtins.property
    @jsii.member(jsii_name="regionalHostedZoneId")
    def regional_hosted_zone_id(self) -> builtins.str:
        '''(experimental) The region-specific Amazon Route 53 Hosted Zone ID of the regional endpoint.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "regionalHostedZoneId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDomainName).__jsii_proxy_class__ = lambda : _IDomainNameProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IHttpApi")
class IHttpApi(IApi, typing_extensions.Protocol):
    '''(experimental) Represents an HTTP API.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="httpApiId")
    def http_api_id(self) -> builtins.str:
        '''(deprecated) The identifier of this API Gateway HTTP API.

        :deprecated: - use apiId instead

        :stability: deprecated
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="addVpcLink")
    def add_vpc_link(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_link_name: typing.Optional[builtins.str] = None,
    ) -> "VpcLink":
        '''(experimental) Add a new VpcLink.

        :param vpc: (experimental) The VPC in which the private resources reside.
        :param security_groups: (experimental) A list of security groups for the VPC link. Default: - no security groups. Use ``addSecurityGroups`` to add security groups
        :param subnets: (experimental) A list of subnets for the VPC link. Default: - private subnets of the provided VPC. Use ``addSubnets`` to add more subnets
        :param vpc_link_name: (experimental) The name used to label and identify the VPC link. Default: - automatically generated name

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricClientError")
    def metric_client_error(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the number of client-side errors captured in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricCount")
    def metric_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the total number API requests in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - SampleCount over 5 minutes

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricDataProcessed")
    def metric_data_processed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the amount of data processed in bytes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricIntegrationLatency")
    def metric_integration_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the time between when API Gateway relays a request to the backend and when it receives a response from the backend.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - no statistic

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricLatency")
    def metric_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) The time between when API Gateway receives a request from a client and when it returns a response to the client.

        The latency includes the integration latency and other API Gateway overhead.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - no statistic

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricServerError")
    def metric_server_error(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the number of server-side errors captured in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes

        :stability: experimental
        '''
        ...


class _IHttpApiProxy(
    jsii.proxy_for(IApi), # type: ignore[misc]
):
    '''(experimental) Represents an HTTP API.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IHttpApi"

    @builtins.property
    @jsii.member(jsii_name="httpApiId")
    def http_api_id(self) -> builtins.str:
        '''(deprecated) The identifier of this API Gateway HTTP API.

        :deprecated: - use apiId instead

        :stability: deprecated
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "httpApiId"))

    @jsii.member(jsii_name="addVpcLink")
    def add_vpc_link(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_link_name: typing.Optional[builtins.str] = None,
    ) -> "VpcLink":
        '''(experimental) Add a new VpcLink.

        :param vpc: (experimental) The VPC in which the private resources reside.
        :param security_groups: (experimental) A list of security groups for the VPC link. Default: - no security groups. Use ``addSecurityGroups`` to add security groups
        :param subnets: (experimental) A list of subnets for the VPC link. Default: - private subnets of the provided VPC. Use ``addSubnets`` to add more subnets
        :param vpc_link_name: (experimental) The name used to label and identify the VPC link. Default: - automatically generated name

        :stability: experimental
        '''
        options = VpcLinkProps(
            vpc=vpc,
            security_groups=security_groups,
            subnets=subnets,
            vpc_link_name=vpc_link_name,
        )

        return typing.cast("VpcLink", jsii.invoke(self, "addVpcLink", [options]))

    @jsii.member(jsii_name="metricClientError")
    def metric_client_error(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the number of client-side errors captured in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricClientError", [props]))

    @jsii.member(jsii_name="metricCount")
    def metric_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the total number API requests in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - SampleCount over 5 minutes

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricCount", [props]))

    @jsii.member(jsii_name="metricDataProcessed")
    def metric_data_processed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the amount of data processed in bytes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricDataProcessed", [props]))

    @jsii.member(jsii_name="metricIntegrationLatency")
    def metric_integration_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the time between when API Gateway relays a request to the backend and when it receives a response from the backend.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - no statistic

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricIntegrationLatency", [props]))

    @jsii.member(jsii_name="metricLatency")
    def metric_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) The time between when API Gateway receives a request from a client and when it returns a response to the client.

        The latency includes the integration latency and other API Gateway overhead.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - no statistic

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricLatency", [props]))

    @jsii.member(jsii_name="metricServerError")
    def metric_server_error(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the number of server-side errors captured in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricServerError", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IHttpApi).__jsii_proxy_class__ = lambda : _IHttpApiProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IHttpAuthorizer")
class IHttpAuthorizer(IAuthorizer, typing_extensions.Protocol):
    '''(experimental) An authorizer for HTTP APIs.

    :stability: experimental
    '''

    pass


class _IHttpAuthorizerProxy(
    jsii.proxy_for(IAuthorizer), # type: ignore[misc]
):
    '''(experimental) An authorizer for HTTP APIs.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IHttpAuthorizer"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IHttpAuthorizer).__jsii_proxy_class__ = lambda : _IHttpAuthorizerProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IHttpRouteAuthorizer")
class IHttpRouteAuthorizer(typing_extensions.Protocol):
    '''(experimental) An authorizer that can attach to an Http Route.

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: "IHttpRoute",
        scope: _constructs_77d1e7e8.Construct,
    ) -> HttpRouteAuthorizerConfig:
        '''(experimental) Bind this authorizer to a specified Http route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        ...


class _IHttpRouteAuthorizerProxy:
    '''(experimental) An authorizer that can attach to an Http Route.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IHttpRouteAuthorizer"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: "IHttpRoute",
        scope: _constructs_77d1e7e8.Construct,
    ) -> HttpRouteAuthorizerConfig:
        '''(experimental) Bind this authorizer to a specified Http route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        options = HttpRouteAuthorizerBindOptions(route=route, scope=scope)

        return typing.cast(HttpRouteAuthorizerConfig, jsii.invoke(self, "bind", [options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IHttpRouteAuthorizer).__jsii_proxy_class__ = lambda : _IHttpRouteAuthorizerProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IIntegration")
class IIntegration(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an integration to an API Route.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="integrationId")
    def integration_id(self) -> builtins.str:
        '''(experimental) Id of the integration.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IIntegrationProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents an integration to an API Route.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IIntegration"

    @builtins.property
    @jsii.member(jsii_name="integrationId")
    def integration_id(self) -> builtins.str:
        '''(experimental) Id of the integration.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "integrationId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IIntegration).__jsii_proxy_class__ = lambda : _IIntegrationProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IMappingValue")
class IMappingValue(typing_extensions.Protocol):
    '''(experimental) Represents a Mapping Value.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        '''(experimental) Represents a Mapping Value.

        :stability: experimental
        '''
        ...


class _IMappingValueProxy:
    '''(experimental) Represents a Mapping Value.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IMappingValue"

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        '''(experimental) Represents a Mapping Value.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "value"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMappingValue).__jsii_proxy_class__ = lambda : _IMappingValueProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IRoute")
class IRoute(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents a route.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="routeId")
    def route_id(self) -> builtins.str:
        '''(experimental) Id of the Route.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IRouteProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents a route.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IRoute"

    @builtins.property
    @jsii.member(jsii_name="routeId")
    def route_id(self) -> builtins.str:
        '''(experimental) Id of the Route.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "routeId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRoute).__jsii_proxy_class__ = lambda : _IRouteProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IStage")
class IStage(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents a Stage.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        '''(experimental) The name of the stage;

        its primary identifier.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''(experimental) The URL to this stage.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this HTTP Api Gateway Stage.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - average over 5 minutes

        :stability: experimental
        '''
        ...


class _IStageProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents a Stage.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IStage"

    @builtins.property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        '''(experimental) The name of the stage;

        its primary identifier.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "stageName"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''(experimental) The URL to this stage.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this HTTP Api Gateway Stage.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - average over 5 minutes

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6eea31b2ea3d8439d0d065d266b0097b8fd2775bebde3b5b7cfc484683aa34a)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStage).__jsii_proxy_class__ = lambda : _IStageProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IVpcLink")
class IVpcLink(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an API Gateway VpcLink.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC to which this VPC Link is associated with.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="vpcLinkId")
    def vpc_link_id(self) -> builtins.str:
        '''(experimental) Physical ID of the VpcLink resource.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IVpcLinkProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents an API Gateway VpcLink.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IVpcLink"

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC to which this VPC Link is associated with.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="vpcLinkId")
    def vpc_link_id(self) -> builtins.str:
        '''(experimental) Physical ID of the VpcLink resource.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "vpcLinkId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IVpcLink).__jsii_proxy_class__ = lambda : _IVpcLinkProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IWebSocketApi")
class IWebSocketApi(IApi, typing_extensions.Protocol):
    '''(experimental) Represents a WebSocket API.

    :stability: experimental
    '''

    pass


class _IWebSocketApiProxy(
    jsii.proxy_for(IApi), # type: ignore[misc]
):
    '''(experimental) Represents a WebSocket API.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IWebSocketApi"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWebSocketApi).__jsii_proxy_class__ = lambda : _IWebSocketApiProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IWebSocketAuthorizer")
class IWebSocketAuthorizer(IAuthorizer, typing_extensions.Protocol):
    '''(experimental) An authorizer for WebSocket APIs.

    :stability: experimental
    '''

    pass


class _IWebSocketAuthorizerProxy(
    jsii.proxy_for(IAuthorizer), # type: ignore[misc]
):
    '''(experimental) An authorizer for WebSocket APIs.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IWebSocketAuthorizer"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWebSocketAuthorizer).__jsii_proxy_class__ = lambda : _IWebSocketAuthorizerProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IWebSocketIntegration")
class IWebSocketIntegration(IIntegration, typing_extensions.Protocol):
    '''(experimental) Represents an Integration for an WebSocket API.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="webSocketApi")
    def web_socket_api(self) -> IWebSocketApi:
        '''(experimental) The WebSocket API associated with this integration.

        :stability: experimental
        '''
        ...


class _IWebSocketIntegrationProxy(
    jsii.proxy_for(IIntegration), # type: ignore[misc]
):
    '''(experimental) Represents an Integration for an WebSocket API.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IWebSocketIntegration"

    @builtins.property
    @jsii.member(jsii_name="webSocketApi")
    def web_socket_api(self) -> IWebSocketApi:
        '''(experimental) The WebSocket API associated with this integration.

        :stability: experimental
        '''
        return typing.cast(IWebSocketApi, jsii.get(self, "webSocketApi"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWebSocketIntegration).__jsii_proxy_class__ = lambda : _IWebSocketIntegrationProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IWebSocketRoute")
class IWebSocketRoute(IRoute, typing_extensions.Protocol):
    '''(experimental) Represents a Route for an WebSocket API.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="routeKey")
    def route_key(self) -> builtins.str:
        '''(experimental) The key to this route.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="webSocketApi")
    def web_socket_api(self) -> IWebSocketApi:
        '''(experimental) The WebSocket API associated with this route.

        :stability: experimental
        '''
        ...


class _IWebSocketRouteProxy(
    jsii.proxy_for(IRoute), # type: ignore[misc]
):
    '''(experimental) Represents a Route for an WebSocket API.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IWebSocketRoute"

    @builtins.property
    @jsii.member(jsii_name="routeKey")
    def route_key(self) -> builtins.str:
        '''(experimental) The key to this route.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "routeKey"))

    @builtins.property
    @jsii.member(jsii_name="webSocketApi")
    def web_socket_api(self) -> IWebSocketApi:
        '''(experimental) The WebSocket API associated with this route.

        :stability: experimental
        '''
        return typing.cast(IWebSocketApi, jsii.get(self, "webSocketApi"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWebSocketRoute).__jsii_proxy_class__ = lambda : _IWebSocketRouteProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IWebSocketRouteAuthorizer")
class IWebSocketRouteAuthorizer(typing_extensions.Protocol):
    '''(experimental) An authorizer that can attach to an WebSocket Route.

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: IWebSocketRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> "WebSocketRouteAuthorizerConfig":
        '''(experimental) Bind this authorizer to a specified WebSocket route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        ...


class _IWebSocketRouteAuthorizerProxy:
    '''(experimental) An authorizer that can attach to an WebSocket Route.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IWebSocketRouteAuthorizer"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: IWebSocketRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> "WebSocketRouteAuthorizerConfig":
        '''(experimental) Bind this authorizer to a specified WebSocket route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        options = WebSocketRouteAuthorizerBindOptions(route=route, scope=scope)

        return typing.cast("WebSocketRouteAuthorizerConfig", jsii.invoke(self, "bind", [options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWebSocketRouteAuthorizer).__jsii_proxy_class__ = lambda : _IWebSocketRouteAuthorizerProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IWebSocketStage")
class IWebSocketStage(IStage, typing_extensions.Protocol):
    '''(experimental) Represents the WebSocketStage.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="api")
    def api(self) -> IWebSocketApi:
        '''(experimental) The API this stage is associated to.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="callbackUrl")
    def callback_url(self) -> builtins.str:
        '''(experimental) The callback URL to this stage.

        You can use the callback URL to send messages to the client from the backend system.
        https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-basic-concept.html
        https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-how-to-call-websocket-api-connections.html

        :stability: experimental
        '''
        ...


class _IWebSocketStageProxy(
    jsii.proxy_for(IStage), # type: ignore[misc]
):
    '''(experimental) Represents the WebSocketStage.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IWebSocketStage"

    @builtins.property
    @jsii.member(jsii_name="api")
    def api(self) -> IWebSocketApi:
        '''(experimental) The API this stage is associated to.

        :stability: experimental
        '''
        return typing.cast(IWebSocketApi, jsii.get(self, "api"))

    @builtins.property
    @jsii.member(jsii_name="callbackUrl")
    def callback_url(self) -> builtins.str:
        '''(experimental) The callback URL to this stage.

        You can use the callback URL to send messages to the client from the backend system.
        https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-basic-concept.html
        https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-how-to-call-websocket-api-connections.html

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "callbackUrl"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWebSocketStage).__jsii_proxy_class__ = lambda : _IWebSocketStageProxy


class IntegrationCredentials(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IntegrationCredentials",
):
    '''(experimental) Credentials used for AWS Service integrations.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
        from aws_cdk import aws_iam as iam
        
        # role: iam.Role
        
        integration_credentials = apigatewayv2_alpha.IntegrationCredentials.from_role(role)
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromRole")
    @builtins.classmethod
    def from_role(
        cls,
        role: _aws_cdk_aws_iam_ceddda9d.IRole,
    ) -> "IntegrationCredentials":
        '''(experimental) Use the specified role for integration requests.

        :param role: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__102c1a776427fd4c0938e5abf575144e45fdb236c63258f1da261499f33717f0)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast("IntegrationCredentials", jsii.sinvoke(cls, "fromRole", [role]))

    @jsii.member(jsii_name="useCallerIdentity")
    @builtins.classmethod
    def use_caller_identity(cls) -> "IntegrationCredentials":
        '''(experimental) Use the calling user's identity to call the integration.

        :stability: experimental
        '''
        return typing.cast("IntegrationCredentials", jsii.sinvoke(cls, "useCallerIdentity", []))

    @builtins.property
    @jsii.member(jsii_name="credentialsArn")
    @abc.abstractmethod
    def credentials_arn(self) -> builtins.str:
        '''(experimental) The ARN of the credentials.

        :stability: experimental
        '''
        ...


class _IntegrationCredentialsProxy(IntegrationCredentials):
    @builtins.property
    @jsii.member(jsii_name="credentialsArn")
    def credentials_arn(self) -> builtins.str:
        '''(experimental) The ARN of the credentials.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "credentialsArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, IntegrationCredentials).__jsii_proxy_class__ = lambda : _IntegrationCredentialsProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.MTLSConfig",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "key": "key", "version": "version"},
)
class MTLSConfig:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        key: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) The mTLS authentication configuration for a custom domain name.

        :param bucket: (experimental) The bucket that the trust store is hosted in.
        :param key: (experimental) The key in S3 to look at for the trust store.
        :param version: (experimental) The version of the S3 object that contains your truststore. To specify a version, you must have versioning enabled for the S3 bucket. Default: - latest version

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_s3 as s3
            import aws_cdk.aws_certificatemanager as acm
            # bucket: s3.Bucket
            
            
            cert_arn = "arn:aws:acm:us-east-1:111111111111:certificate"
            domain_name = "example.com"
            
            apigwv2.DomainName(self, "DomainName",
                domain_name=domain_name,
                certificate=acm.Certificate.from_certificate_arn(self, "cert", cert_arn),
                mtls=apigwv2.MTLSConfig(
                    bucket=bucket,
                    key="someca.pem",
                    version="version"
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38e19f865daecac4e9c0b7840b549ee7e3e17328107146b6aeed11be416a4830)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "key": key,
        }
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''(experimental) The bucket that the trust store is hosted in.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''(experimental) The key in S3 to look at for the trust store.

        :stability: experimental
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of the S3 object that contains your truststore.

        To specify a version, you must have versioning enabled for the S3 bucket.

        :default: - latest version

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MTLSConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IMappingValue)
class MappingValue(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.MappingValue",
):
    '''(experimental) Represents a Mapping Value.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpAlbIntegration
        
        # lb: elbv2.ApplicationLoadBalancer
        
        listener = lb.add_listener("listener", port=80)
        listener.add_targets("target",
            port=80
        )
        
        http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
            default_integration=HttpAlbIntegration("DefaultIntegration", listener,
                parameter_mapping=apigwv2.ParameterMapping().append_header("header2", apigwv2.MappingValue.request_header("header1")).remove_header("header1")
            )
        )
    '''

    def __init__(self, value: builtins.str) -> None:
        '''
        :param value: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__214070b3203c10af4bde0b28ed256ac9a4d24597f026dd0b0cc830dd88c3212d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.create(self.__class__, self, [value])

    @jsii.member(jsii_name="contextVariable")
    @builtins.classmethod
    def context_variable(cls, variable_name: builtins.str) -> "MappingValue":
        '''(experimental) Creates a context variable mapping value.

        :param variable_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4af933305aeacd390d336f32a5829afa054de657121385d6ec7753a9ea26d601)
            check_type(argname="argument variable_name", value=variable_name, expected_type=type_hints["variable_name"])
        return typing.cast("MappingValue", jsii.sinvoke(cls, "contextVariable", [variable_name]))

    @jsii.member(jsii_name="custom")
    @builtins.classmethod
    def custom(cls, value: builtins.str) -> "MappingValue":
        '''(experimental) Creates a custom mapping value.

        :param value: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ea57d3eb4bcfb04e995828dff02ab6f0787305f407450d33b5272726fe121ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("MappingValue", jsii.sinvoke(cls, "custom", [value]))

    @jsii.member(jsii_name="requestBody")
    @builtins.classmethod
    def request_body(cls, name: builtins.str) -> "MappingValue":
        '''(experimental) Creates a request body mapping value.

        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd491365abe2954925b1f433ba7521a56e4bbc0bcdfddd61b667ca4f13903681)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("MappingValue", jsii.sinvoke(cls, "requestBody", [name]))

    @jsii.member(jsii_name="requestHeader")
    @builtins.classmethod
    def request_header(cls, name: builtins.str) -> "MappingValue":
        '''(experimental) Creates a header mapping value.

        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e720451078130f0098a0b48416451612a00e6befa0c802ff75a2b864085649a5)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("MappingValue", jsii.sinvoke(cls, "requestHeader", [name]))

    @jsii.member(jsii_name="requestPath")
    @builtins.classmethod
    def request_path(cls) -> "MappingValue":
        '''(experimental) Creates a request path mapping value.

        :stability: experimental
        '''
        return typing.cast("MappingValue", jsii.sinvoke(cls, "requestPath", []))

    @jsii.member(jsii_name="requestPathParam")
    @builtins.classmethod
    def request_path_param(cls, name: builtins.str) -> "MappingValue":
        '''(experimental) Creates a request path parameter mapping value.

        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69c384039069eb05e230de4bc9ac53925e0d361bd038ed0a3b02e073b1525c71)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("MappingValue", jsii.sinvoke(cls, "requestPathParam", [name]))

    @jsii.member(jsii_name="requestQueryString")
    @builtins.classmethod
    def request_query_string(cls, name: builtins.str) -> "MappingValue":
        '''(experimental) Creates a query string mapping value.

        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b36b16773b8a1c554f9a57b9e3d7a3722f155a3d65b1a10b4204ac3f1740616a)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("MappingValue", jsii.sinvoke(cls, "requestQueryString", [name]))

    @jsii.member(jsii_name="stageVariable")
    @builtins.classmethod
    def stage_variable(cls, variable_name: builtins.str) -> "MappingValue":
        '''(experimental) Creates a stage variable mapping value.

        :param variable_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3602fe53f550a6f339115089310b50937eb494d182495b9b3787a639c5dcaed)
            check_type(argname="argument variable_name", value=variable_name, expected_type=type_hints["variable_name"])
        return typing.cast("MappingValue", jsii.sinvoke(cls, "stageVariable", [variable_name]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="NONE")
    def NONE(cls) -> "MappingValue":
        '''(experimental) Creates an empty mapping value.

        :stability: experimental
        '''
        return typing.cast("MappingValue", jsii.sget(cls, "NONE"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        '''(experimental) Represents a Mapping Value.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "value"))


class ParameterMapping(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.ParameterMapping",
):
    '''(experimental) Represents a Parameter Mapping.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpAlbIntegration
        
        # lb: elbv2.ApplicationLoadBalancer
        
        listener = lb.add_listener("listener", port=80)
        listener.add_targets("target",
            port=80
        )
        
        http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
            default_integration=HttpAlbIntegration("DefaultIntegration", listener,
                parameter_mapping=apigwv2.ParameterMapping().append_header("header2", apigwv2.MappingValue.request_header("header1")).remove_header("header1")
            )
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromObject")
    @builtins.classmethod
    def from_object(
        cls,
        obj: typing.Mapping[builtins.str, MappingValue],
    ) -> "ParameterMapping":
        '''(experimental) Creates a mapping from an object.

        :param obj: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8181ef9cc8308f9477f0a1caad591787ed40d80e9353a4ab806411f93450058)
            check_type(argname="argument obj", value=obj, expected_type=type_hints["obj"])
        return typing.cast("ParameterMapping", jsii.sinvoke(cls, "fromObject", [obj]))

    @jsii.member(jsii_name="appendHeader")
    def append_header(
        self,
        name: builtins.str,
        value: MappingValue,
    ) -> "ParameterMapping":
        '''(experimental) Creates a mapping to append a header.

        :param name: -
        :param value: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56ae57cc9968fa2fd30ad1d66784260b0e784ac1e0ae80923fa737f9a8ada22a)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("ParameterMapping", jsii.invoke(self, "appendHeader", [name, value]))

    @jsii.member(jsii_name="appendQueryString")
    def append_query_string(
        self,
        name: builtins.str,
        value: MappingValue,
    ) -> "ParameterMapping":
        '''(experimental) Creates a mapping to append a query string.

        :param name: -
        :param value: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f855f9472042f201eb931ccc90ac6f72c3684fdf5485ee6979662f843ed27cc)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("ParameterMapping", jsii.invoke(self, "appendQueryString", [name, value]))

    @jsii.member(jsii_name="custom")
    def custom(self, key: builtins.str, value: builtins.str) -> "ParameterMapping":
        '''(experimental) Creates a custom mapping.

        :param key: -
        :param value: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea27856048c8e84cddc832b14d9115403f2b80ce39008d1d2a456c126be689c6)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("ParameterMapping", jsii.invoke(self, "custom", [key, value]))

    @jsii.member(jsii_name="overwriteHeader")
    def overwrite_header(
        self,
        name: builtins.str,
        value: MappingValue,
    ) -> "ParameterMapping":
        '''(experimental) Creates a mapping to overwrite a header.

        :param name: -
        :param value: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bbf5124407bf24ea9fa7d17aa1565a5ed9210655f4f602da854ad14a24db0d5)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("ParameterMapping", jsii.invoke(self, "overwriteHeader", [name, value]))

    @jsii.member(jsii_name="overwritePath")
    def overwrite_path(self, value: MappingValue) -> "ParameterMapping":
        '''(experimental) Creates a mapping to overwrite a path.

        :param value: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3969677f031f21644ed17215886d65e2445e67dcf22241b2a6150248c6192f36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("ParameterMapping", jsii.invoke(self, "overwritePath", [value]))

    @jsii.member(jsii_name="overwriteQueryString")
    def overwrite_query_string(
        self,
        name: builtins.str,
        value: MappingValue,
    ) -> "ParameterMapping":
        '''(experimental) Creates a mapping to overwrite a querystring.

        :param name: -
        :param value: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e75c515536f95796a2a8f985b00f7829f0664a04b9a30bed03ea9ad1ce892d91)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("ParameterMapping", jsii.invoke(self, "overwriteQueryString", [name, value]))

    @jsii.member(jsii_name="removeHeader")
    def remove_header(self, name: builtins.str) -> "ParameterMapping":
        '''(experimental) Creates a mapping to remove a header.

        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48411845428e2e72182038805ca1f55aa523a254158b3148ec49d4ee874decc5)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("ParameterMapping", jsii.invoke(self, "removeHeader", [name]))

    @jsii.member(jsii_name="removeQueryString")
    def remove_query_string(self, name: builtins.str) -> "ParameterMapping":
        '''(experimental) Creates a mapping to remove a querystring.

        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46e584a752980831919a8156516ab93f44fb1a783b5798270ff450fdc6bc50d2)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("ParameterMapping", jsii.invoke(self, "removeQueryString", [name]))

    @builtins.property
    @jsii.member(jsii_name="mappings")
    def mappings(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) Represents all created parameter mappings.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "mappings"))


class PayloadFormatVersion(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.PayloadFormatVersion",
):
    '''(experimental) Payload format version for lambda proxy integration.

    :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
        
        payload_format_version = apigatewayv2_alpha.PayloadFormatVersion.custom("version")
    '''

    @jsii.member(jsii_name="custom")
    @builtins.classmethod
    def custom(cls, version: builtins.str) -> "PayloadFormatVersion":
        '''(experimental) A custom payload version.

        Typically used if there is a version number that the CDK doesn't support yet

        :param version: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__650e7e8cf5095b5caf036d1cdfea61cdc50d05db4e0b82311e5988ab562c7508)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        return typing.cast("PayloadFormatVersion", jsii.sinvoke(cls, "custom", [version]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="VERSION_1_0")
    def VERSION_1_0(cls) -> "PayloadFormatVersion":
        '''(experimental) Version 1.0.

        :stability: experimental
        '''
        return typing.cast("PayloadFormatVersion", jsii.sget(cls, "VERSION_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="VERSION_2_0")
    def VERSION_2_0(cls) -> "PayloadFormatVersion":
        '''(experimental) Version 2.0.

        :stability: experimental
        '''
        return typing.cast("PayloadFormatVersion", jsii.sget(cls, "VERSION_2_0"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''(experimental) version as a string.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))


@jsii.enum(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.SecurityPolicy")
class SecurityPolicy(enum.Enum):
    '''(experimental) The minimum version of the SSL protocol that you want API Gateway to use for HTTPS connections.

    :stability: experimental
    '''

    TLS_1_0 = "TLS_1_0"
    '''(experimental) Cipher suite TLS 1.0.

    :stability: experimental
    '''
    TLS_1_2 = "TLS_1_2"
    '''(experimental) Cipher suite TLS 1.2.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.StageAttributes",
    jsii_struct_bases=[],
    name_mapping={"stage_name": "stageName"},
)
class StageAttributes:
    def __init__(self, *, stage_name: builtins.str) -> None:
        '''(experimental) The attributes used to import existing Stage.

        :param stage_name: (experimental) The name of the stage.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            stage_attributes = apigatewayv2_alpha.StageAttributes(
                stage_name="stageName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7bc86d60b044b6ce8b75e1e701218c18bc2ca9ef7cc2a9667e4858066891f46)
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stage_name": stage_name,
        }

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''(experimental) The name of the stage.

        :stability: experimental
        '''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StageAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.StageOptions",
    jsii_struct_bases=[],
    name_mapping={
        "auto_deploy": "autoDeploy",
        "domain_mapping": "domainMapping",
        "throttle": "throttle",
    },
)
class StageOptions:
    def __init__(
        self,
        *,
        auto_deploy: typing.Optional[builtins.bool] = None,
        domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        throttle: typing.Optional[typing.Union["ThrottleSettings", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Options required to create a new stage.

        Options that are common between HTTP and Websocket APIs.

        :param auto_deploy: (experimental) Whether updates to an API automatically trigger a new deployment. Default: false
        :param domain_mapping: (experimental) The options for custom domain and api mapping. Default: - no custom domain and api mapping configuration
        :param throttle: (experimental) Throttle settings for the routes of this stage. Default: - no throttling configuration

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            # domain_name: apigatewayv2_alpha.DomainName
            
            stage_options = apigatewayv2_alpha.StageOptions(
                auto_deploy=False,
                domain_mapping=apigatewayv2_alpha.DomainMappingOptions(
                    domain_name=domain_name,
            
                    # the properties below are optional
                    mapping_key="mappingKey"
                ),
                throttle=apigatewayv2_alpha.ThrottleSettings(
                    burst_limit=123,
                    rate_limit=123
                )
            )
        '''
        if isinstance(domain_mapping, dict):
            domain_mapping = DomainMappingOptions(**domain_mapping)
        if isinstance(throttle, dict):
            throttle = ThrottleSettings(**throttle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a32c0806cbd09e57e1b6cb67e4b59ac7fdd424ef31f824f2caeda822945dbf65)
            check_type(argname="argument auto_deploy", value=auto_deploy, expected_type=type_hints["auto_deploy"])
            check_type(argname="argument domain_mapping", value=domain_mapping, expected_type=type_hints["domain_mapping"])
            check_type(argname="argument throttle", value=throttle, expected_type=type_hints["throttle"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auto_deploy is not None:
            self._values["auto_deploy"] = auto_deploy
        if domain_mapping is not None:
            self._values["domain_mapping"] = domain_mapping
        if throttle is not None:
            self._values["throttle"] = throttle

    @builtins.property
    def auto_deploy(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether updates to an API automatically trigger a new deployment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("auto_deploy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain_mapping(self) -> typing.Optional[DomainMappingOptions]:
        '''(experimental) The options for custom domain and api mapping.

        :default: - no custom domain and api mapping configuration

        :stability: experimental
        '''
        result = self._values.get("domain_mapping")
        return typing.cast(typing.Optional[DomainMappingOptions], result)

    @builtins.property
    def throttle(self) -> typing.Optional["ThrottleSettings"]:
        '''(experimental) Throttle settings for the routes of this stage.

        :default: - no throttling configuration

        :stability: experimental
        '''
        result = self._values.get("throttle")
        return typing.cast(typing.Optional["ThrottleSettings"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.ThrottleSettings",
    jsii_struct_bases=[],
    name_mapping={"burst_limit": "burstLimit", "rate_limit": "rateLimit"},
)
class ThrottleSettings:
    def __init__(
        self,
        *,
        burst_limit: typing.Optional[jsii.Number] = None,
        rate_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Container for defining throttling parameters to API stages.

        :param burst_limit: (experimental) The maximum API request rate limit over a time ranging from one to a few seconds. Default: none
        :param rate_limit: (experimental) The API request steady-state rate limit (average requests per second over an extended period of time). Default: none

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            throttle_settings = apigatewayv2_alpha.ThrottleSettings(
                burst_limit=123,
                rate_limit=123
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ad556ef4d84d522901264cb64a96b656171558870186a72f596567dc19746a2)
            check_type(argname="argument burst_limit", value=burst_limit, expected_type=type_hints["burst_limit"])
            check_type(argname="argument rate_limit", value=rate_limit, expected_type=type_hints["rate_limit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if burst_limit is not None:
            self._values["burst_limit"] = burst_limit
        if rate_limit is not None:
            self._values["rate_limit"] = rate_limit

    @builtins.property
    def burst_limit(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum API request rate limit over a time ranging from one to a few seconds.

        :default: none

        :stability: experimental
        '''
        result = self._values.get("burst_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rate_limit(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The API request steady-state rate limit (average requests per second over an extended period of time).

        :default: none

        :stability: experimental
        '''
        result = self._values.get("rate_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ThrottleSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IVpcLink)
class VpcLink(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.VpcLink",
):
    '''(experimental) Define a new VPC Link Specifies an API Gateway VPC link for a HTTP API to access resources in an Amazon Virtual Private Cloud (VPC).

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_ec2 as ec2
        
        
        vpc = ec2.Vpc(self, "VPC")
        vpc_link = apigwv2.VpcLink(self, "VpcLink", vpc=vpc)
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_link_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: (experimental) The VPC in which the private resources reside.
        :param security_groups: (experimental) A list of security groups for the VPC link. Default: - no security groups. Use ``addSecurityGroups`` to add security groups
        :param subnets: (experimental) A list of subnets for the VPC link. Default: - private subnets of the provided VPC. Use ``addSubnets`` to add more subnets
        :param vpc_link_name: (experimental) The name used to label and identify the VPC link. Default: - automatically generated name

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7e5cf8ebb393b1b711349f32ce6a5d91c23aa92cb3f1a5fb324d1ace8fa39e5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = VpcLinkProps(
            vpc=vpc,
            security_groups=security_groups,
            subnets=subnets,
            vpc_link_name=vpc_link_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromVpcLinkAttributes")
    @builtins.classmethod
    def from_vpc_link_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        vpc_link_id: builtins.str,
    ) -> IVpcLink:
        '''(experimental) Import a VPC Link by specifying its attributes.

        :param scope: -
        :param id: -
        :param vpc: (experimental) The VPC to which this VPC link is associated with.
        :param vpc_link_id: (experimental) The VPC Link id.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1b73cd3902808dcd9cedbbb002791b3c0b71ecf07dc9ee537153e45a37de0b7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = VpcLinkAttributes(vpc=vpc, vpc_link_id=vpc_link_id)

        return typing.cast(IVpcLink, jsii.sinvoke(cls, "fromVpcLinkAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addSecurityGroups")
    def add_security_groups(
        self,
        *groups: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
    ) -> None:
        '''(experimental) Adds the provided security groups to the vpc link.

        :param groups: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb1536c4a56444b87ed12cf12ec84dcad1aeea01af7e687ab6bc5440355e7e11)
            check_type(argname="argument groups", value=groups, expected_type=typing.Tuple[type_hints["groups"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "addSecurityGroups", [*groups]))

    @jsii.member(jsii_name="addSubnets")
    def add_subnets(self, *subnets: _aws_cdk_aws_ec2_ceddda9d.ISubnet) -> None:
        '''(experimental) Adds the provided subnets to the vpc link.

        :param subnets: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b26d604e4ca1a2688579e0987cdb68ab389de0e4b8cb68e274ece105bdd03cf)
            check_type(argname="argument subnets", value=subnets, expected_type=typing.Tuple[type_hints["subnets"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "addSubnets", [*subnets]))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC to which this VPC Link is associated with.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="vpcLinkId")
    def vpc_link_id(self) -> builtins.str:
        '''(experimental) Physical ID of the VpcLink resource.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "vpcLinkId"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.VpcLinkAttributes",
    jsii_struct_bases=[],
    name_mapping={"vpc": "vpc", "vpc_link_id": "vpcLinkId"},
)
class VpcLinkAttributes:
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        vpc_link_id: builtins.str,
    ) -> None:
        '''(experimental) Attributes when importing a new VpcLink.

        :param vpc: (experimental) The VPC to which this VPC link is associated with.
        :param vpc_link_id: (experimental) The VPC Link id.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_ec2 as ec2
            
            # vpc: ec2.Vpc
            
            awesome_link = apigwv2.VpcLink.from_vpc_link_attributes(self, "awesome-vpc-link",
                vpc_link_id="us-east-1_oiuR12Abd",
                vpc=vpc
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b806190a5cb732ad4de67d21bd895caa64bb12248a0d0ab31634597e02c8057e)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_link_id", value=vpc_link_id, expected_type=type_hints["vpc_link_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
            "vpc_link_id": vpc_link_id,
        }

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC to which this VPC link is associated with.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def vpc_link_id(self) -> builtins.str:
        '''(experimental) The VPC Link id.

        :stability: experimental
        '''
        result = self._values.get("vpc_link_id")
        assert result is not None, "Required property 'vpc_link_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpcLinkAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.VpcLinkProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "security_groups": "securityGroups",
        "subnets": "subnets",
        "vpc_link_name": "vpcLinkName",
    },
)
class VpcLinkProps:
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_link_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a VpcLink.

        :param vpc: (experimental) The VPC in which the private resources reside.
        :param security_groups: (experimental) A list of security groups for the VPC link. Default: - no security groups. Use ``addSecurityGroups`` to add security groups
        :param subnets: (experimental) A list of subnets for the VPC link. Default: - private subnets of the provided VPC. Use ``addSubnets`` to add more subnets
        :param vpc_link_name: (experimental) The name used to label and identify the VPC link. Default: - automatically generated name

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_ec2 as ec2
            
            
            vpc = ec2.Vpc(self, "VPC")
            vpc_link = apigwv2.VpcLink(self, "VpcLink", vpc=vpc)
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9aed9118f19188de6967aa0373708cfcd4ffb3d828b567d6cbc01404c7aa6581)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc_link_name", value=vpc_link_name, expected_type=type_hints["vpc_link_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnets is not None:
            self._values["subnets"] = subnets
        if vpc_link_name is not None:
            self._values["vpc_link_name"] = vpc_link_name

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC in which the private resources reside.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''(experimental) A list of security groups for the VPC link.

        :default: - no security groups. Use ``addSecurityGroups`` to add security groups

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) A list of subnets for the VPC link.

        :default: - private subnets of the provided VPC. Use ``addSubnets`` to add more subnets

        :stability: experimental
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc_link_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name used to label and identify the VPC link.

        :default: - automatically generated name

        :stability: experimental
        '''
        result = self._values.get("vpc_link_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpcLinkProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IWebSocketApi, IApi)
class WebSocketApi(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketApi",
):
    '''(experimental) Create a new API Gateway WebSocket API endpoint.

    :stability: experimental
    :resource: AWS::ApiGatewayV2::Api
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration
        
        # message_handler: lambda.Function
        
        
        web_socket_api = apigwv2.WebSocketApi(self, "mywsapi")
        apigwv2.WebSocketStage(self, "mystage",
            web_socket_api=web_socket_api,
            stage_name="dev",
            auto_deploy=True
        )
        web_socket_api.add_route("sendmessage",
            integration=WebSocketLambdaIntegration("SendMessageIntegration", message_handler)
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api_key_selection_expression: typing.Optional["WebSocketApiKeySelectionExpression"] = None,
        api_name: typing.Optional[builtins.str] = None,
        connect_route_options: typing.Optional[typing.Union["WebSocketRouteOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        default_route_options: typing.Optional[typing.Union["WebSocketRouteOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        disconnect_route_options: typing.Optional[typing.Union["WebSocketRouteOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        route_selection_expression: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api_key_selection_expression: (experimental) An API key selection expression. Providing this option will require an API Key be provided to access the API. Default: - Key is not required to access these APIs
        :param api_name: (experimental) Name for the WebSocket API resource. Default: - id of the WebSocketApi construct.
        :param connect_route_options: (experimental) Options to configure a '$connect' route. Default: - no '$connect' route configured
        :param default_route_options: (experimental) Options to configure a '$default' route. Default: - no '$default' route configured
        :param description: (experimental) The description of the API. Default: - none
        :param disconnect_route_options: (experimental) Options to configure a '$disconnect' route. Default: - no '$disconnect' route configured
        :param route_selection_expression: (experimental) The route selection expression for the API. Default: '$request.body.action'

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1178cce7f52c6ba72b835087f977643630d7f0c2665b967ecfee0bfe59093cb6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WebSocketApiProps(
            api_key_selection_expression=api_key_selection_expression,
            api_name=api_name,
            connect_route_options=connect_route_options,
            default_route_options=default_route_options,
            description=description,
            disconnect_route_options=disconnect_route_options,
            route_selection_expression=route_selection_expression,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromWebSocketApiAttributes")
    @builtins.classmethod
    def from_web_socket_api_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        web_socket_id: builtins.str,
        api_endpoint: typing.Optional[builtins.str] = None,
    ) -> IWebSocketApi:
        '''(experimental) Import an existing WebSocket API into this CDK app.

        :param scope: -
        :param id: -
        :param web_socket_id: (experimental) The identifier of the WebSocketApi.
        :param api_endpoint: (experimental) The endpoint URL of the WebSocketApi. Default: - throw san error if apiEndpoint is accessed.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53d1a9fe1fdf41c0b5a739761d4875fb19c206a09c26c51425f989503e6b976b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = WebSocketApiAttributes(
            web_socket_id=web_socket_id, api_endpoint=api_endpoint
        )

        return typing.cast(IWebSocketApi, jsii.sinvoke(cls, "fromWebSocketApiAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addRoute")
    def add_route(
        self,
        route_key: builtins.str,
        *,
        integration: "WebSocketRouteIntegration",
        authorizer: typing.Optional[IWebSocketRouteAuthorizer] = None,
    ) -> "WebSocketRoute":
        '''(experimental) Add a new route.

        :param route_key: -
        :param integration: (experimental) The integration to be configured on this route.
        :param authorizer: (experimental) The authorize to this route. You can only set authorizer to a $connect route. Default: - No Authorizer

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3fea69a2469b346680a0c3465ad0d8edf75af46ec799894b3faabfa5c26ec77)
            check_type(argname="argument route_key", value=route_key, expected_type=type_hints["route_key"])
        options = WebSocketRouteOptions(integration=integration, authorizer=authorizer)

        return typing.cast("WebSocketRoute", jsii.invoke(self, "addRoute", [route_key, options]))

    @jsii.member(jsii_name="grantManageConnections")
    def grant_manage_connections(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant access to the API Gateway management API for this WebSocket API to an IAM principal (Role/Group/User).

        :param identity: The principal.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3519e657dc5ef6b61e34eb3fc9f6d114f2ebbf762f5ca278412f276b78b73bd7)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantManageConnections", [identity]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this Api Gateway.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25c26b71a707cd073d476cfe86d40884d0adc369830b3b667bfcc8d3d5069fe3)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @builtins.property
    @jsii.member(jsii_name="apiEndpoint")
    def api_endpoint(self) -> builtins.str:
        '''(experimental) The default endpoint for an API.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''(experimental) The identifier of this API Gateway API.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @builtins.property
    @jsii.member(jsii_name="webSocketApiName")
    def web_socket_api_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A human friendly name for this WebSocket API.

        Note that this is different from ``webSocketApiId``.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webSocketApiName"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketApiAttributes",
    jsii_struct_bases=[],
    name_mapping={"web_socket_id": "webSocketId", "api_endpoint": "apiEndpoint"},
)
class WebSocketApiAttributes:
    def __init__(
        self,
        *,
        web_socket_id: builtins.str,
        api_endpoint: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Attributes for importing a WebSocketApi into the CDK.

        :param web_socket_id: (experimental) The identifier of the WebSocketApi.
        :param api_endpoint: (experimental) The endpoint URL of the WebSocketApi. Default: - throw san error if apiEndpoint is accessed.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            web_socket_api = apigwv2.WebSocketApi.from_web_socket_api_attributes(self, "mywsapi", web_socket_id="api-1234")
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae0c8df0ca0e715101942e90c3ba6802a24a7d17b7ccaf420c2de7498d0f3110)
            check_type(argname="argument web_socket_id", value=web_socket_id, expected_type=type_hints["web_socket_id"])
            check_type(argname="argument api_endpoint", value=api_endpoint, expected_type=type_hints["api_endpoint"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "web_socket_id": web_socket_id,
        }
        if api_endpoint is not None:
            self._values["api_endpoint"] = api_endpoint

    @builtins.property
    def web_socket_id(self) -> builtins.str:
        '''(experimental) The identifier of the WebSocketApi.

        :stability: experimental
        '''
        result = self._values.get("web_socket_id")
        assert result is not None, "Required property 'web_socket_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_endpoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) The endpoint URL of the WebSocketApi.

        :default: - throw san error if apiEndpoint is accessed.

        :stability: experimental
        '''
        result = self._values.get("api_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketApiAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WebSocketApiKeySelectionExpression(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketApiKeySelectionExpression",
):
    '''(experimental) Represents the currently available API Key Selection Expressions.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        web_socket_api = apigwv2.WebSocketApi(self, "mywsapi",
            api_key_selection_expression=apigwv2.WebSocketApiKeySelectionExpression.HEADER_X_API_KEY
        )
    '''

    def __init__(self, custom_api_key_selector: builtins.str) -> None:
        '''
        :param custom_api_key_selector: The expression used by API Gateway.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34791e0880629c49a9f044c4e76a43e531d8704f81a7f9c57e446e0f8af0541c)
            check_type(argname="argument custom_api_key_selector", value=custom_api_key_selector, expected_type=type_hints["custom_api_key_selector"])
        jsii.create(self.__class__, self, [custom_api_key_selector])

    @jsii.python.classproperty
    @jsii.member(jsii_name="AUTHORIZER_USAGE_IDENTIFIER_KEY")
    def AUTHORIZER_USAGE_IDENTIFIER_KEY(cls) -> "WebSocketApiKeySelectionExpression":
        '''(experimental) The API will extract the key value from the ``usageIdentifierKey`` attribute in the ``context`` map, returned by the Lambda Authorizer.

        See https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-lambda-authorizer-output.html

        :stability: experimental
        '''
        return typing.cast("WebSocketApiKeySelectionExpression", jsii.sget(cls, "AUTHORIZER_USAGE_IDENTIFIER_KEY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HEADER_X_API_KEY")
    def HEADER_X_API_KEY(cls) -> "WebSocketApiKeySelectionExpression":
        '''(experimental) The API will extract the key value from the ``x-api-key`` header in the user request.

        :stability: experimental
        '''
        return typing.cast("WebSocketApiKeySelectionExpression", jsii.sget(cls, "HEADER_X_API_KEY"))

    @builtins.property
    @jsii.member(jsii_name="customApiKeySelector")
    def custom_api_key_selector(self) -> builtins.str:
        '''(experimental) The expression used by API Gateway.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "customApiKeySelector"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketApiProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_key_selection_expression": "apiKeySelectionExpression",
        "api_name": "apiName",
        "connect_route_options": "connectRouteOptions",
        "default_route_options": "defaultRouteOptions",
        "description": "description",
        "disconnect_route_options": "disconnectRouteOptions",
        "route_selection_expression": "routeSelectionExpression",
    },
)
class WebSocketApiProps:
    def __init__(
        self,
        *,
        api_key_selection_expression: typing.Optional[WebSocketApiKeySelectionExpression] = None,
        api_name: typing.Optional[builtins.str] = None,
        connect_route_options: typing.Optional[typing.Union["WebSocketRouteOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        default_route_options: typing.Optional[typing.Union["WebSocketRouteOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        disconnect_route_options: typing.Optional[typing.Union["WebSocketRouteOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        route_selection_expression: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Props for WebSocket API.

        :param api_key_selection_expression: (experimental) An API key selection expression. Providing this option will require an API Key be provided to access the API. Default: - Key is not required to access these APIs
        :param api_name: (experimental) Name for the WebSocket API resource. Default: - id of the WebSocketApi construct.
        :param connect_route_options: (experimental) Options to configure a '$connect' route. Default: - no '$connect' route configured
        :param default_route_options: (experimental) Options to configure a '$default' route. Default: - no '$default' route configured
        :param description: (experimental) The description of the API. Default: - none
        :param disconnect_route_options: (experimental) Options to configure a '$disconnect' route. Default: - no '$disconnect' route configured
        :param route_selection_expression: (experimental) The route selection expression for the API. Default: '$request.body.action'

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.aws_apigatewayv2_authorizers_alpha import WebSocketLambdaAuthorizer
            from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration
            
            # This function handles your auth logic
            # auth_handler: lambda.Function
            
            # This function handles your WebSocket requests
            # handler: lambda.Function
            
            
            authorizer = WebSocketLambdaAuthorizer("Authorizer", auth_handler)
            
            integration = WebSocketLambdaIntegration("Integration", handler)
            
            apigwv2.WebSocketApi(self, "WebSocketApi",
                connect_route_options=apigwv2.WebSocketRouteOptions(
                    integration=integration,
                    authorizer=authorizer
                )
            )
        '''
        if isinstance(connect_route_options, dict):
            connect_route_options = WebSocketRouteOptions(**connect_route_options)
        if isinstance(default_route_options, dict):
            default_route_options = WebSocketRouteOptions(**default_route_options)
        if isinstance(disconnect_route_options, dict):
            disconnect_route_options = WebSocketRouteOptions(**disconnect_route_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92cd23b712e91b17d8d403f5d44376505198f2e4d79f2370e3ce6a05ea6ddc2a)
            check_type(argname="argument api_key_selection_expression", value=api_key_selection_expression, expected_type=type_hints["api_key_selection_expression"])
            check_type(argname="argument api_name", value=api_name, expected_type=type_hints["api_name"])
            check_type(argname="argument connect_route_options", value=connect_route_options, expected_type=type_hints["connect_route_options"])
            check_type(argname="argument default_route_options", value=default_route_options, expected_type=type_hints["default_route_options"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disconnect_route_options", value=disconnect_route_options, expected_type=type_hints["disconnect_route_options"])
            check_type(argname="argument route_selection_expression", value=route_selection_expression, expected_type=type_hints["route_selection_expression"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if api_key_selection_expression is not None:
            self._values["api_key_selection_expression"] = api_key_selection_expression
        if api_name is not None:
            self._values["api_name"] = api_name
        if connect_route_options is not None:
            self._values["connect_route_options"] = connect_route_options
        if default_route_options is not None:
            self._values["default_route_options"] = default_route_options
        if description is not None:
            self._values["description"] = description
        if disconnect_route_options is not None:
            self._values["disconnect_route_options"] = disconnect_route_options
        if route_selection_expression is not None:
            self._values["route_selection_expression"] = route_selection_expression

    @builtins.property
    def api_key_selection_expression(
        self,
    ) -> typing.Optional[WebSocketApiKeySelectionExpression]:
        '''(experimental) An API key selection expression.

        Providing this option will require an API Key be provided to access the API.

        :default: - Key is not required to access these APIs

        :stability: experimental
        '''
        result = self._values.get("api_key_selection_expression")
        return typing.cast(typing.Optional[WebSocketApiKeySelectionExpression], result)

    @builtins.property
    def api_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name for the WebSocket API resource.

        :default: - id of the WebSocketApi construct.

        :stability: experimental
        '''
        result = self._values.get("api_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connect_route_options(self) -> typing.Optional["WebSocketRouteOptions"]:
        '''(experimental) Options to configure a '$connect' route.

        :default: - no '$connect' route configured

        :stability: experimental
        '''
        result = self._values.get("connect_route_options")
        return typing.cast(typing.Optional["WebSocketRouteOptions"], result)

    @builtins.property
    def default_route_options(self) -> typing.Optional["WebSocketRouteOptions"]:
        '''(experimental) Options to configure a '$default' route.

        :default: - no '$default' route configured

        :stability: experimental
        '''
        result = self._values.get("default_route_options")
        return typing.cast(typing.Optional["WebSocketRouteOptions"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the API.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disconnect_route_options(self) -> typing.Optional["WebSocketRouteOptions"]:
        '''(experimental) Options to configure a '$disconnect' route.

        :default: - no '$disconnect' route configured

        :stability: experimental
        '''
        result = self._values.get("disconnect_route_options")
        return typing.cast(typing.Optional["WebSocketRouteOptions"], result)

    @builtins.property
    def route_selection_expression(self) -> typing.Optional[builtins.str]:
        '''(experimental) The route selection expression for the API.

        :default: '$request.body.action'

        :stability: experimental
        '''
        result = self._values.get("route_selection_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IWebSocketAuthorizer)
class WebSocketAuthorizer(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketAuthorizer",
):
    '''(experimental) An authorizer for WebSocket Apis.

    :stability: experimental
    :resource: AWS::ApiGatewayV2::Authorizer
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
        
        # web_socket_api: apigatewayv2_alpha.WebSocketApi
        
        web_socket_authorizer = apigatewayv2_alpha.WebSocketAuthorizer(self, "MyWebSocketAuthorizer",
            identity_source=["identitySource"],
            type=apigatewayv2_alpha.WebSocketAuthorizerType.LAMBDA,
            web_socket_api=web_socket_api,
        
            # the properties below are optional
            authorizer_name="authorizerName",
            authorizer_uri="authorizerUri"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        identity_source: typing.Sequence[builtins.str],
        type: "WebSocketAuthorizerType",
        web_socket_api: IWebSocketApi,
        authorizer_name: typing.Optional[builtins.str] = None,
        authorizer_uri: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param identity_source: (experimental) The identity source for which authorization is requested.
        :param type: (experimental) The type of authorizer.
        :param web_socket_api: (experimental) WebSocket Api to attach the authorizer to.
        :param authorizer_name: (experimental) Name of the authorizer. Default: - id of the WebSocketAuthorizer construct.
        :param authorizer_uri: (experimental) The authorizer's Uniform Resource Identifier (URI). For REQUEST authorizers, this must be a well-formed Lambda function URI. Default: - required for Request authorizer types

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f24f7e7421170c9759c052f1d385a1f7e94dbd5eb18e0b47be9cab3ee8826990)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WebSocketAuthorizerProps(
            identity_source=identity_source,
            type=type,
            web_socket_api=web_socket_api,
            authorizer_name=authorizer_name,
            authorizer_uri=authorizer_uri,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromWebSocketAuthorizerAttributes")
    @builtins.classmethod
    def from_web_socket_authorizer_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        authorizer_id: builtins.str,
        authorizer_type: builtins.str,
    ) -> IWebSocketRouteAuthorizer:
        '''(experimental) Import an existing WebSocket Authorizer into this CDK app.

        :param scope: -
        :param id: -
        :param authorizer_id: (experimental) Id of the Authorizer.
        :param authorizer_type: (experimental) Type of authorizer. Possible values are: - CUSTOM - Lambda Authorizer - NONE - No Authorization

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e383ace2ee0471b5314c8dcb5e8b4c903443f7f45d06e85ce1160c2494ade7c3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = WebSocketAuthorizerAttributes(
            authorizer_id=authorizer_id, authorizer_type=authorizer_type
        )

        return typing.cast(IWebSocketRouteAuthorizer, jsii.sinvoke(cls, "fromWebSocketAuthorizerAttributes", [scope, id, attrs]))

    @builtins.property
    @jsii.member(jsii_name="authorizerId")
    def authorizer_id(self) -> builtins.str:
        '''(experimental) Id of the Authorizer.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "authorizerId"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketAuthorizerAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_id": "authorizerId",
        "authorizer_type": "authorizerType",
    },
)
class WebSocketAuthorizerAttributes:
    def __init__(
        self,
        *,
        authorizer_id: builtins.str,
        authorizer_type: builtins.str,
    ) -> None:
        '''(experimental) Reference to an WebSocket authorizer.

        :param authorizer_id: (experimental) Id of the Authorizer.
        :param authorizer_type: (experimental) Type of authorizer. Possible values are: - CUSTOM - Lambda Authorizer - NONE - No Authorization

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            web_socket_authorizer_attributes = apigatewayv2_alpha.WebSocketAuthorizerAttributes(
                authorizer_id="authorizerId",
                authorizer_type="authorizerType"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec6cd687f35d4560bc6ed8b97968247261b8e88313cf6380b0c261222b1d373c)
            check_type(argname="argument authorizer_id", value=authorizer_id, expected_type=type_hints["authorizer_id"])
            check_type(argname="argument authorizer_type", value=authorizer_type, expected_type=type_hints["authorizer_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authorizer_id": authorizer_id,
            "authorizer_type": authorizer_type,
        }

    @builtins.property
    def authorizer_id(self) -> builtins.str:
        '''(experimental) Id of the Authorizer.

        :stability: experimental
        '''
        result = self._values.get("authorizer_id")
        assert result is not None, "Required property 'authorizer_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorizer_type(self) -> builtins.str:
        '''(experimental) Type of authorizer.

        Possible values are:

        - CUSTOM - Lambda Authorizer
        - NONE - No Authorization

        :stability: experimental
        '''
        result = self._values.get("authorizer_type")
        assert result is not None, "Required property 'authorizer_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketAuthorizerAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "identity_source": "identitySource",
        "type": "type",
        "web_socket_api": "webSocketApi",
        "authorizer_name": "authorizerName",
        "authorizer_uri": "authorizerUri",
    },
)
class WebSocketAuthorizerProps:
    def __init__(
        self,
        *,
        identity_source: typing.Sequence[builtins.str],
        type: "WebSocketAuthorizerType",
        web_socket_api: IWebSocketApi,
        authorizer_name: typing.Optional[builtins.str] = None,
        authorizer_uri: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties to initialize an instance of ``WebSocketAuthorizer``.

        :param identity_source: (experimental) The identity source for which authorization is requested.
        :param type: (experimental) The type of authorizer.
        :param web_socket_api: (experimental) WebSocket Api to attach the authorizer to.
        :param authorizer_name: (experimental) Name of the authorizer. Default: - id of the WebSocketAuthorizer construct.
        :param authorizer_uri: (experimental) The authorizer's Uniform Resource Identifier (URI). For REQUEST authorizers, this must be a well-formed Lambda function URI. Default: - required for Request authorizer types

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            # web_socket_api: apigatewayv2_alpha.WebSocketApi
            
            web_socket_authorizer_props = apigatewayv2_alpha.WebSocketAuthorizerProps(
                identity_source=["identitySource"],
                type=apigatewayv2_alpha.WebSocketAuthorizerType.LAMBDA,
                web_socket_api=web_socket_api,
            
                # the properties below are optional
                authorizer_name="authorizerName",
                authorizer_uri="authorizerUri"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e02c909494ad68823621decb1cf4f3c9d5a9383ba2429deace659f406a376cde)
            check_type(argname="argument identity_source", value=identity_source, expected_type=type_hints["identity_source"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument web_socket_api", value=web_socket_api, expected_type=type_hints["web_socket_api"])
            check_type(argname="argument authorizer_name", value=authorizer_name, expected_type=type_hints["authorizer_name"])
            check_type(argname="argument authorizer_uri", value=authorizer_uri, expected_type=type_hints["authorizer_uri"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identity_source": identity_source,
            "type": type,
            "web_socket_api": web_socket_api,
        }
        if authorizer_name is not None:
            self._values["authorizer_name"] = authorizer_name
        if authorizer_uri is not None:
            self._values["authorizer_uri"] = authorizer_uri

    @builtins.property
    def identity_source(self) -> typing.List[builtins.str]:
        '''(experimental) The identity source for which authorization is requested.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-identitysource
        :stability: experimental
        '''
        result = self._values.get("identity_source")
        assert result is not None, "Required property 'identity_source' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def type(self) -> "WebSocketAuthorizerType":
        '''(experimental) The type of authorizer.

        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("WebSocketAuthorizerType", result)

    @builtins.property
    def web_socket_api(self) -> IWebSocketApi:
        '''(experimental) WebSocket Api to attach the authorizer to.

        :stability: experimental
        '''
        result = self._values.get("web_socket_api")
        assert result is not None, "Required property 'web_socket_api' is missing"
        return typing.cast(IWebSocketApi, result)

    @builtins.property
    def authorizer_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the authorizer.

        :default: - id of the WebSocketAuthorizer construct.

        :stability: experimental
        '''
        result = self._values.get("authorizer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authorizer_uri(self) -> typing.Optional[builtins.str]:
        '''(experimental) The authorizer's Uniform Resource Identifier (URI).

        For REQUEST authorizers, this must be a well-formed Lambda function URI.

        :default: - required for Request authorizer types

        :stability: experimental
        '''
        result = self._values.get("authorizer_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketAuthorizerType")
class WebSocketAuthorizerType(enum.Enum):
    '''(experimental) Supported Authorizer types.

    :stability: experimental
    '''

    LAMBDA = "LAMBDA"
    '''(experimental) Lambda Authorizer.

    :stability: experimental
    '''
    IAM = "IAM"
    '''(experimental) IAM Authorizer.

    :stability: experimental
    '''


@jsii.implements(IWebSocketIntegration)
class WebSocketIntegration(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketIntegration",
):
    '''(experimental) The integration for an API route.

    :stability: experimental
    :resource: AWS::ApiGatewayV2::Integration
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
        
        # web_socket_api: apigatewayv2_alpha.WebSocketApi
        
        web_socket_integration = apigatewayv2_alpha.WebSocketIntegration(self, "MyWebSocketIntegration",
            integration_type=apigatewayv2_alpha.WebSocketIntegrationType.AWS_PROXY,
            integration_uri="integrationUri",
            web_socket_api=web_socket_api
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        integration_type: "WebSocketIntegrationType",
        integration_uri: builtins.str,
        web_socket_api: IWebSocketApi,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param integration_type: (experimental) Integration type.
        :param integration_uri: (experimental) Integration URI.
        :param web_socket_api: (experimental) The WebSocket API to which this integration should be bound.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__870fc94d82010681246ecba710a6ed2fbd784a22488897490747220c5a9bb1a9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WebSocketIntegrationProps(
            integration_type=integration_type,
            integration_uri=integration_uri,
            web_socket_api=web_socket_api,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="integrationId")
    def integration_id(self) -> builtins.str:
        '''(experimental) Id of the integration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "integrationId"))

    @builtins.property
    @jsii.member(jsii_name="webSocketApi")
    def web_socket_api(self) -> IWebSocketApi:
        '''(experimental) The WebSocket API associated with this integration.

        :stability: experimental
        '''
        return typing.cast(IWebSocketApi, jsii.get(self, "webSocketApi"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketIntegrationProps",
    jsii_struct_bases=[],
    name_mapping={
        "integration_type": "integrationType",
        "integration_uri": "integrationUri",
        "web_socket_api": "webSocketApi",
    },
)
class WebSocketIntegrationProps:
    def __init__(
        self,
        *,
        integration_type: "WebSocketIntegrationType",
        integration_uri: builtins.str,
        web_socket_api: IWebSocketApi,
    ) -> None:
        '''(experimental) The integration properties.

        :param integration_type: (experimental) Integration type.
        :param integration_uri: (experimental) Integration URI.
        :param web_socket_api: (experimental) The WebSocket API to which this integration should be bound.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            # web_socket_api: apigatewayv2_alpha.WebSocketApi
            
            web_socket_integration_props = apigatewayv2_alpha.WebSocketIntegrationProps(
                integration_type=apigatewayv2_alpha.WebSocketIntegrationType.AWS_PROXY,
                integration_uri="integrationUri",
                web_socket_api=web_socket_api
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__809d7a61872d8b86104362e83bf279e0275cab4ee56d78bb981f42a476435905)
            check_type(argname="argument integration_type", value=integration_type, expected_type=type_hints["integration_type"])
            check_type(argname="argument integration_uri", value=integration_uri, expected_type=type_hints["integration_uri"])
            check_type(argname="argument web_socket_api", value=web_socket_api, expected_type=type_hints["web_socket_api"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration_type": integration_type,
            "integration_uri": integration_uri,
            "web_socket_api": web_socket_api,
        }

    @builtins.property
    def integration_type(self) -> "WebSocketIntegrationType":
        '''(experimental) Integration type.

        :stability: experimental
        '''
        result = self._values.get("integration_type")
        assert result is not None, "Required property 'integration_type' is missing"
        return typing.cast("WebSocketIntegrationType", result)

    @builtins.property
    def integration_uri(self) -> builtins.str:
        '''(experimental) Integration URI.

        :stability: experimental
        '''
        result = self._values.get("integration_uri")
        assert result is not None, "Required property 'integration_uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def web_socket_api(self) -> IWebSocketApi:
        '''(experimental) The WebSocket API to which this integration should be bound.

        :stability: experimental
        '''
        result = self._values.get("web_socket_api")
        assert result is not None, "Required property 'web_socket_api' is missing"
        return typing.cast(IWebSocketApi, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketIntegrationType")
class WebSocketIntegrationType(enum.Enum):
    '''(experimental) WebSocket Integration Types.

    :stability: experimental
    '''

    AWS_PROXY = "AWS_PROXY"
    '''(experimental) AWS Proxy Integration Type.

    :stability: experimental
    '''
    MOCK = "MOCK"
    '''(experimental) Mock Integration Type.

    :stability: experimental
    '''


@jsii.implements(IWebSocketRouteAuthorizer)
class WebSocketNoneAuthorizer(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketNoneAuthorizer",
):
    '''(experimental) Explicitly configure no authorizers on specific WebSocket API routes.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
        
        web_socket_none_authorizer = apigatewayv2_alpha.WebSocketNoneAuthorizer()
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: IWebSocketRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> "WebSocketRouteAuthorizerConfig":
        '''(experimental) Bind this authorizer to a specified WebSocket route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        _ = WebSocketRouteAuthorizerBindOptions(route=route, scope=scope)

        return typing.cast("WebSocketRouteAuthorizerConfig", jsii.invoke(self, "bind", [_]))


@jsii.implements(IWebSocketRoute)
class WebSocketRoute(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketRoute",
):
    '''(experimental) Route class that creates the Route for API Gateway WebSocket API.

    :stability: experimental
    :resource: AWS::ApiGatewayV2::Route
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
        
        # web_socket_api: apigatewayv2_alpha.WebSocketApi
        # web_socket_route_authorizer: apigatewayv2_alpha.IWebSocketRouteAuthorizer
        # web_socket_route_integration: apigatewayv2_alpha.WebSocketRouteIntegration
        
        web_socket_route = apigatewayv2_alpha.WebSocketRoute(self, "MyWebSocketRoute",
            integration=web_socket_route_integration,
            route_key="routeKey",
            web_socket_api=web_socket_api,
        
            # the properties below are optional
            api_key_required=False,
            authorizer=web_socket_route_authorizer
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        route_key: builtins.str,
        web_socket_api: IWebSocketApi,
        api_key_required: typing.Optional[builtins.bool] = None,
        integration: "WebSocketRouteIntegration",
        authorizer: typing.Optional[IWebSocketRouteAuthorizer] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param route_key: (experimental) The key to this route.
        :param web_socket_api: (experimental) The API the route is associated with.
        :param api_key_required: (experimental) Whether the route requires an API Key to be provided. Default: false
        :param integration: (experimental) The integration to be configured on this route.
        :param authorizer: (experimental) The authorize to this route. You can only set authorizer to a $connect route. Default: - No Authorizer

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89ed8dea5fd2abdd3d7348cec8375728ea8c56911ab73c2e7661f42936a36951)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WebSocketRouteProps(
            route_key=route_key,
            web_socket_api=web_socket_api,
            api_key_required=api_key_required,
            integration=integration,
            authorizer=authorizer,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="routeId")
    def route_id(self) -> builtins.str:
        '''(experimental) Id of the Route.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "routeId"))

    @builtins.property
    @jsii.member(jsii_name="routeKey")
    def route_key(self) -> builtins.str:
        '''(experimental) The key to this route.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "routeKey"))

    @builtins.property
    @jsii.member(jsii_name="webSocketApi")
    def web_socket_api(self) -> IWebSocketApi:
        '''(experimental) The WebSocket API associated with this route.

        :stability: experimental
        '''
        return typing.cast(IWebSocketApi, jsii.get(self, "webSocketApi"))

    @builtins.property
    @jsii.member(jsii_name="integrationResponseId")
    def integration_response_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) Integration response ID.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationResponseId"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketRouteAuthorizerBindOptions",
    jsii_struct_bases=[],
    name_mapping={"route": "route", "scope": "scope"},
)
class WebSocketRouteAuthorizerBindOptions:
    def __init__(
        self,
        *,
        route: IWebSocketRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> None:
        '''(experimental) Input to the bind() operation, that binds an authorizer to a route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            import constructs as constructs
            
            # construct: constructs.Construct
            # web_socket_route: apigatewayv2_alpha.WebSocketRoute
            
            web_socket_route_authorizer_bind_options = apigatewayv2_alpha.WebSocketRouteAuthorizerBindOptions(
                route=web_socket_route,
                scope=construct
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fccd4465748920ec078ce3c095e6d5997201164b60c9937b341677d4bed18d2d)
            check_type(argname="argument route", value=route, expected_type=type_hints["route"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "route": route,
            "scope": scope,
        }

    @builtins.property
    def route(self) -> IWebSocketRoute:
        '''(experimental) The route to which the authorizer is being bound.

        :stability: experimental
        '''
        result = self._values.get("route")
        assert result is not None, "Required property 'route' is missing"
        return typing.cast(IWebSocketRoute, result)

    @builtins.property
    def scope(self) -> _constructs_77d1e7e8.Construct:
        '''(experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(_constructs_77d1e7e8.Construct, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketRouteAuthorizerBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketRouteAuthorizerConfig",
    jsii_struct_bases=[],
    name_mapping={
        "authorization_type": "authorizationType",
        "authorizer_id": "authorizerId",
    },
)
class WebSocketRouteAuthorizerConfig:
    def __init__(
        self,
        *,
        authorization_type: builtins.str,
        authorizer_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Results of binding an authorizer to an WebSocket route.

        :param authorization_type: (experimental) The type of authorization. Possible values are: - CUSTOM - Lambda Authorizer - NONE - No Authorization
        :param authorizer_id: (experimental) The authorizer id. Default: - No authorizer id (useful for AWS_IAM route authorizer)

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            web_socket_route_authorizer_config = apigatewayv2_alpha.WebSocketRouteAuthorizerConfig(
                authorization_type="authorizationType",
            
                # the properties below are optional
                authorizer_id="authorizerId"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31b7978ca3879b28e59655ad191a6a2a4b1f15e48c662e792f29609537418e7b)
            check_type(argname="argument authorization_type", value=authorization_type, expected_type=type_hints["authorization_type"])
            check_type(argname="argument authorizer_id", value=authorizer_id, expected_type=type_hints["authorizer_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authorization_type": authorization_type,
        }
        if authorizer_id is not None:
            self._values["authorizer_id"] = authorizer_id

    @builtins.property
    def authorization_type(self) -> builtins.str:
        '''(experimental) The type of authorization.

        Possible values are:

        - CUSTOM - Lambda Authorizer
        - NONE - No Authorization

        :stability: experimental
        '''
        result = self._values.get("authorization_type")
        assert result is not None, "Required property 'authorization_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorizer_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The authorizer id.

        :default: - No authorizer id (useful for AWS_IAM route authorizer)

        :stability: experimental
        '''
        result = self._values.get("authorizer_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketRouteAuthorizerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WebSocketRouteIntegration(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketRouteIntegration",
):
    '''(experimental) The interface that various route integration classes will inherit.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration
        
        # message_handler: lambda.Function
        
        
        web_socket_api = apigwv2.WebSocketApi(self, "mywsapi")
        apigwv2.WebSocketStage(self, "mystage",
            web_socket_api=web_socket_api,
            stage_name="dev",
            auto_deploy=True
        )
        web_socket_api.add_route("sendmessage",
            integration=WebSocketLambdaIntegration("SendMessageIntegration", message_handler)
        )
    '''

    def __init__(self, id: builtins.str) -> None:
        '''(experimental) Initialize an integration for a route on websocket api.

        :param id: id of the underlying ``WebSocketIntegration`` construct.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c197ca72497cd4c42d540f6e0560e6883980b3d825f1228e227525877aff3ac4)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [id])

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def bind(
        self,
        *,
        route: IWebSocketRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> "WebSocketRouteIntegrationConfig":
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``WebSocketRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        ...


class _WebSocketRouteIntegrationProxy(WebSocketRouteIntegration):
    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: IWebSocketRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> "WebSocketRouteIntegrationConfig":
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``WebSocketRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = WebSocketRouteIntegrationBindOptions(route=route, scope=scope)

        return typing.cast("WebSocketRouteIntegrationConfig", jsii.invoke(self, "bind", [options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, WebSocketRouteIntegration).__jsii_proxy_class__ = lambda : _WebSocketRouteIntegrationProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketRouteIntegrationBindOptions",
    jsii_struct_bases=[],
    name_mapping={"route": "route", "scope": "scope"},
)
class WebSocketRouteIntegrationBindOptions:
    def __init__(
        self,
        *,
        route: IWebSocketRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> None:
        '''(experimental) Options to the WebSocketRouteIntegration during its bind operation.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``WebSocketRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            import constructs as constructs
            
            # construct: constructs.Construct
            # web_socket_route: apigatewayv2_alpha.WebSocketRoute
            
            web_socket_route_integration_bind_options = apigatewayv2_alpha.WebSocketRouteIntegrationBindOptions(
                route=web_socket_route,
                scope=construct
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9af6c9ac36dba4ed1e02e99de4fc973a26bd4423e8609681f9bddbf43144cd7)
            check_type(argname="argument route", value=route, expected_type=type_hints["route"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "route": route,
            "scope": scope,
        }

    @builtins.property
    def route(self) -> IWebSocketRoute:
        '''(experimental) The route to which this is being bound.

        :stability: experimental
        '''
        result = self._values.get("route")
        assert result is not None, "Required property 'route' is missing"
        return typing.cast(IWebSocketRoute, result)

    @builtins.property
    def scope(self) -> _constructs_77d1e7e8.Construct:
        '''(experimental) The current scope in which the bind is occurring.

        If the ``WebSocketRouteIntegration`` being bound creates additional constructs,
        this will be used as their parent scope.

        :stability: experimental
        '''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(_constructs_77d1e7e8.Construct, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketRouteIntegrationBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketRouteIntegrationConfig",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "uri": "uri"},
)
class WebSocketRouteIntegrationConfig:
    def __init__(self, *, type: WebSocketIntegrationType, uri: builtins.str) -> None:
        '''(experimental) Config returned back as a result of the bind.

        :param type: (experimental) Integration type.
        :param uri: (experimental) Integration URI.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            web_socket_route_integration_config = apigatewayv2_alpha.WebSocketRouteIntegrationConfig(
                type=apigatewayv2_alpha.WebSocketIntegrationType.AWS_PROXY,
                uri="uri"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9151ff6a777a4992f010dc6dd1747375682b7a6c0d45bfbda07ab180448bf7f)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument uri", value=uri, expected_type=type_hints["uri"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
            "uri": uri,
        }

    @builtins.property
    def type(self) -> WebSocketIntegrationType:
        '''(experimental) Integration type.

        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(WebSocketIntegrationType, result)

    @builtins.property
    def uri(self) -> builtins.str:
        '''(experimental) Integration URI.

        :stability: experimental
        '''
        result = self._values.get("uri")
        assert result is not None, "Required property 'uri' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketRouteIntegrationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketRouteOptions",
    jsii_struct_bases=[],
    name_mapping={"integration": "integration", "authorizer": "authorizer"},
)
class WebSocketRouteOptions:
    def __init__(
        self,
        *,
        integration: WebSocketRouteIntegration,
        authorizer: typing.Optional[IWebSocketRouteAuthorizer] = None,
    ) -> None:
        '''(experimental) Options used to add route to the API.

        :param integration: (experimental) The integration to be configured on this route.
        :param authorizer: (experimental) The authorize to this route. You can only set authorizer to a $connect route. Default: - No Authorizer

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration
            
            # message_handler: lambda.Function
            
            
            web_socket_api = apigwv2.WebSocketApi(self, "mywsapi")
            apigwv2.WebSocketStage(self, "mystage",
                web_socket_api=web_socket_api,
                stage_name="dev",
                auto_deploy=True
            )
            web_socket_api.add_route("sendmessage",
                integration=WebSocketLambdaIntegration("SendMessageIntegration", message_handler)
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__015136d7cb99d78ecaebab742d43a14edcb81e619d7967b3b64eaf687c0d9ee3)
            check_type(argname="argument integration", value=integration, expected_type=type_hints["integration"])
            check_type(argname="argument authorizer", value=authorizer, expected_type=type_hints["authorizer"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration": integration,
        }
        if authorizer is not None:
            self._values["authorizer"] = authorizer

    @builtins.property
    def integration(self) -> WebSocketRouteIntegration:
        '''(experimental) The integration to be configured on this route.

        :stability: experimental
        '''
        result = self._values.get("integration")
        assert result is not None, "Required property 'integration' is missing"
        return typing.cast(WebSocketRouteIntegration, result)

    @builtins.property
    def authorizer(self) -> typing.Optional[IWebSocketRouteAuthorizer]:
        '''(experimental) The authorize to this route.

        You can only set authorizer to a $connect route.

        :default: - No Authorizer

        :stability: experimental
        '''
        result = self._values.get("authorizer")
        return typing.cast(typing.Optional[IWebSocketRouteAuthorizer], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketRouteOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketRouteProps",
    jsii_struct_bases=[WebSocketRouteOptions],
    name_mapping={
        "integration": "integration",
        "authorizer": "authorizer",
        "route_key": "routeKey",
        "web_socket_api": "webSocketApi",
        "api_key_required": "apiKeyRequired",
    },
)
class WebSocketRouteProps(WebSocketRouteOptions):
    def __init__(
        self,
        *,
        integration: WebSocketRouteIntegration,
        authorizer: typing.Optional[IWebSocketRouteAuthorizer] = None,
        route_key: builtins.str,
        web_socket_api: IWebSocketApi,
        api_key_required: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties to initialize a new Route.

        :param integration: (experimental) The integration to be configured on this route.
        :param authorizer: (experimental) The authorize to this route. You can only set authorizer to a $connect route. Default: - No Authorizer
        :param route_key: (experimental) The key to this route.
        :param web_socket_api: (experimental) The API the route is associated with.
        :param api_key_required: (experimental) Whether the route requires an API Key to be provided. Default: false

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            # web_socket_api: apigatewayv2_alpha.WebSocketApi
            # web_socket_route_authorizer: apigatewayv2_alpha.IWebSocketRouteAuthorizer
            # web_socket_route_integration: apigatewayv2_alpha.WebSocketRouteIntegration
            
            web_socket_route_props = apigatewayv2_alpha.WebSocketRouteProps(
                integration=web_socket_route_integration,
                route_key="routeKey",
                web_socket_api=web_socket_api,
            
                # the properties below are optional
                api_key_required=False,
                authorizer=web_socket_route_authorizer
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16bac6f0c09166c97608a842bf64940ba77c4a2c9803f76985adfdc50657856b)
            check_type(argname="argument integration", value=integration, expected_type=type_hints["integration"])
            check_type(argname="argument authorizer", value=authorizer, expected_type=type_hints["authorizer"])
            check_type(argname="argument route_key", value=route_key, expected_type=type_hints["route_key"])
            check_type(argname="argument web_socket_api", value=web_socket_api, expected_type=type_hints["web_socket_api"])
            check_type(argname="argument api_key_required", value=api_key_required, expected_type=type_hints["api_key_required"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration": integration,
            "route_key": route_key,
            "web_socket_api": web_socket_api,
        }
        if authorizer is not None:
            self._values["authorizer"] = authorizer
        if api_key_required is not None:
            self._values["api_key_required"] = api_key_required

    @builtins.property
    def integration(self) -> WebSocketRouteIntegration:
        '''(experimental) The integration to be configured on this route.

        :stability: experimental
        '''
        result = self._values.get("integration")
        assert result is not None, "Required property 'integration' is missing"
        return typing.cast(WebSocketRouteIntegration, result)

    @builtins.property
    def authorizer(self) -> typing.Optional[IWebSocketRouteAuthorizer]:
        '''(experimental) The authorize to this route.

        You can only set authorizer to a $connect route.

        :default: - No Authorizer

        :stability: experimental
        '''
        result = self._values.get("authorizer")
        return typing.cast(typing.Optional[IWebSocketRouteAuthorizer], result)

    @builtins.property
    def route_key(self) -> builtins.str:
        '''(experimental) The key to this route.

        :stability: experimental
        '''
        result = self._values.get("route_key")
        assert result is not None, "Required property 'route_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def web_socket_api(self) -> IWebSocketApi:
        '''(experimental) The API the route is associated with.

        :stability: experimental
        '''
        result = self._values.get("web_socket_api")
        assert result is not None, "Required property 'web_socket_api' is missing"
        return typing.cast(IWebSocketApi, result)

    @builtins.property
    def api_key_required(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the route requires an API Key to be provided.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("api_key_required")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketRouteProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IWebSocketStage, IStage)
class WebSocketStage(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketStage",
):
    '''(experimental) Represents a stage where an instance of the API is deployed.

    :stability: experimental
    :resource: AWS::ApiGatewayV2::Stage
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration
        
        # message_handler: lambda.Function
        
        
        web_socket_api = apigwv2.WebSocketApi(self, "mywsapi")
        apigwv2.WebSocketStage(self, "mystage",
            web_socket_api=web_socket_api,
            stage_name="dev",
            auto_deploy=True
        )
        web_socket_api.add_route("sendmessage",
            integration=WebSocketLambdaIntegration("SendMessageIntegration", message_handler)
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        stage_name: builtins.str,
        web_socket_api: IWebSocketApi,
        auto_deploy: typing.Optional[builtins.bool] = None,
        domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param stage_name: (experimental) The name of the stage.
        :param web_socket_api: (experimental) The WebSocket API to which this stage is associated.
        :param auto_deploy: (experimental) Whether updates to an API automatically trigger a new deployment. Default: false
        :param domain_mapping: (experimental) The options for custom domain and api mapping. Default: - no custom domain and api mapping configuration
        :param throttle: (experimental) Throttle settings for the routes of this stage. Default: - no throttling configuration

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48af0e7d3ce9ece527270c25928990cf8b605f1e3585927c1afcc3ffef087cf6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WebSocketStageProps(
            stage_name=stage_name,
            web_socket_api=web_socket_api,
            auto_deploy=auto_deploy,
            domain_mapping=domain_mapping,
            throttle=throttle,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromWebSocketStageAttributes")
    @builtins.classmethod
    def from_web_socket_stage_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api: IWebSocketApi,
        stage_name: builtins.str,
    ) -> IWebSocketStage:
        '''(experimental) Import an existing stage into this CDK app.

        :param scope: -
        :param id: -
        :param api: (experimental) The API to which this stage is associated.
        :param stage_name: (experimental) The name of the stage.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96d2e4a524a0487b6a3e41257302724f03ec2dea315215c2348c1e882d82a509)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = WebSocketStageAttributes(api=api, stage_name=stage_name)

        return typing.cast(IWebSocketStage, jsii.sinvoke(cls, "fromWebSocketStageAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="grantManagementApiAccess")
    def grant_management_api_access(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant access to the API Gateway management API for this WebSocket API Stage to an IAM principal (Role/Group/User).

        :param identity: The principal.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__385987aac133337ee8f5f880408bf66af8f3e3a5651bc827a3bc5af110334a17)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantManagementApiAccess", [identity]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this HTTP Api Gateway Stage.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b080276ad15c8223193f7ed4fefbc76be9f47841814221e9a4dee06286100c93)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @builtins.property
    @jsii.member(jsii_name="api")
    def api(self) -> IWebSocketApi:
        '''(experimental) The API this stage is associated to.

        :stability: experimental
        '''
        return typing.cast(IWebSocketApi, jsii.get(self, "api"))

    @builtins.property
    @jsii.member(jsii_name="baseApi")
    def _base_api(self) -> IApi:
        '''
        :stability: experimental
        '''
        return typing.cast(IApi, jsii.get(self, "baseApi"))

    @builtins.property
    @jsii.member(jsii_name="callbackUrl")
    def callback_url(self) -> builtins.str:
        '''(experimental) The callback URL to this stage.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "callbackUrl"))

    @builtins.property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        '''(experimental) The name of the stage;

        its primary identifier.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "stageName"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''(experimental) The websocket URL to this stage.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "url"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketStageAttributes",
    jsii_struct_bases=[StageAttributes],
    name_mapping={"stage_name": "stageName", "api": "api"},
)
class WebSocketStageAttributes(StageAttributes):
    def __init__(self, *, stage_name: builtins.str, api: IWebSocketApi) -> None:
        '''(experimental) The attributes used to import existing WebSocketStage.

        :param stage_name: (experimental) The name of the stage.
        :param api: (experimental) The API to which this stage is associated.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            # web_socket_api: apigatewayv2_alpha.WebSocketApi
            
            web_socket_stage_attributes = apigatewayv2_alpha.WebSocketStageAttributes(
                api=web_socket_api,
                stage_name="stageName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e391865a4ae4984a049207c6b5c3768117999fb528b5847ca1a6c7c35d2f82b)
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument api", value=api, expected_type=type_hints["api"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stage_name": stage_name,
            "api": api,
        }

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''(experimental) The name of the stage.

        :stability: experimental
        '''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api(self) -> IWebSocketApi:
        '''(experimental) The API to which this stage is associated.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(IWebSocketApi, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketStageAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.WebSocketStageProps",
    jsii_struct_bases=[StageOptions],
    name_mapping={
        "auto_deploy": "autoDeploy",
        "domain_mapping": "domainMapping",
        "throttle": "throttle",
        "stage_name": "stageName",
        "web_socket_api": "webSocketApi",
    },
)
class WebSocketStageProps(StageOptions):
    def __init__(
        self,
        *,
        auto_deploy: typing.Optional[builtins.bool] = None,
        domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        stage_name: builtins.str,
        web_socket_api: IWebSocketApi,
    ) -> None:
        '''(experimental) Properties to initialize an instance of ``WebSocketStage``.

        :param auto_deploy: (experimental) Whether updates to an API automatically trigger a new deployment. Default: false
        :param domain_mapping: (experimental) The options for custom domain and api mapping. Default: - no custom domain and api mapping configuration
        :param throttle: (experimental) Throttle settings for the routes of this stage. Default: - no throttling configuration
        :param stage_name: (experimental) The name of the stage.
        :param web_socket_api: (experimental) The WebSocket API to which this stage is associated.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration
            
            # message_handler: lambda.Function
            
            
            web_socket_api = apigwv2.WebSocketApi(self, "mywsapi")
            apigwv2.WebSocketStage(self, "mystage",
                web_socket_api=web_socket_api,
                stage_name="dev",
                auto_deploy=True
            )
            web_socket_api.add_route("sendmessage",
                integration=WebSocketLambdaIntegration("SendMessageIntegration", message_handler)
            )
        '''
        if isinstance(domain_mapping, dict):
            domain_mapping = DomainMappingOptions(**domain_mapping)
        if isinstance(throttle, dict):
            throttle = ThrottleSettings(**throttle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__782ab449d8fa4cf0a46fbab6526bdc241efef3893414586af02c8f715748ee2a)
            check_type(argname="argument auto_deploy", value=auto_deploy, expected_type=type_hints["auto_deploy"])
            check_type(argname="argument domain_mapping", value=domain_mapping, expected_type=type_hints["domain_mapping"])
            check_type(argname="argument throttle", value=throttle, expected_type=type_hints["throttle"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument web_socket_api", value=web_socket_api, expected_type=type_hints["web_socket_api"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stage_name": stage_name,
            "web_socket_api": web_socket_api,
        }
        if auto_deploy is not None:
            self._values["auto_deploy"] = auto_deploy
        if domain_mapping is not None:
            self._values["domain_mapping"] = domain_mapping
        if throttle is not None:
            self._values["throttle"] = throttle

    @builtins.property
    def auto_deploy(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether updates to an API automatically trigger a new deployment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("auto_deploy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain_mapping(self) -> typing.Optional[DomainMappingOptions]:
        '''(experimental) The options for custom domain and api mapping.

        :default: - no custom domain and api mapping configuration

        :stability: experimental
        '''
        result = self._values.get("domain_mapping")
        return typing.cast(typing.Optional[DomainMappingOptions], result)

    @builtins.property
    def throttle(self) -> typing.Optional[ThrottleSettings]:
        '''(experimental) Throttle settings for the routes of this stage.

        :default: - no throttling configuration

        :stability: experimental
        '''
        result = self._values.get("throttle")
        return typing.cast(typing.Optional[ThrottleSettings], result)

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''(experimental) The name of the stage.

        :stability: experimental
        '''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def web_socket_api(self) -> IWebSocketApi:
        '''(experimental) The WebSocket API to which this stage is associated.

        :stability: experimental
        '''
        result = self._values.get("web_socket_api")
        assert result is not None, "Required property 'web_socket_api' is missing"
        return typing.cast(IWebSocketApi, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.AddRoutesOptions",
    jsii_struct_bases=[BatchHttpRouteOptions],
    name_mapping={
        "integration": "integration",
        "path": "path",
        "authorization_scopes": "authorizationScopes",
        "authorizer": "authorizer",
        "methods": "methods",
    },
)
class AddRoutesOptions(BatchHttpRouteOptions):
    def __init__(
        self,
        *,
        integration: HttpRouteIntegration,
        path: builtins.str,
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        authorizer: typing.Optional[IHttpRouteAuthorizer] = None,
        methods: typing.Optional[typing.Sequence[HttpMethod]] = None,
    ) -> None:
        '''(experimental) Options for the Route with Integration resource.

        :param integration: (experimental) The integration to be configured on this route.
        :param path: (experimental) The path at which all of these routes are configured.
        :param authorization_scopes: (experimental) The list of OIDC scopes to include in the authorization. These scopes will override the default authorization scopes on the gateway. Set to [] to remove default scopes Default: - uses defaultAuthorizationScopes if configured on the API, otherwise none.
        :param authorizer: (experimental) Authorizer to be associated to these routes. Use NoneAuthorizer to remove the default authorizer for the api Default: - uses the default authorizer if one is specified on the HttpApi
        :param methods: (experimental) The HTTP methods to be configured. Default: HttpMethod.ANY

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpLambdaAuthorizer, HttpLambdaResponseType
            from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration
            
            # This function handles your auth logic
            # auth_handler: lambda.Function
            
            
            authorizer = HttpLambdaAuthorizer("BooksAuthorizer", auth_handler,
                response_types=[HttpLambdaResponseType.SIMPLE]
            )
            
            api = apigwv2.HttpApi(self, "HttpApi")
            
            api.add_routes(
                integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.example.com"),
                path="/books",
                authorizer=authorizer
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca8141f667bdde01ab0100d57a58a21f4b9acc231a1bbfb55a1925c258a680c6)
            check_type(argname="argument integration", value=integration, expected_type=type_hints["integration"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument authorization_scopes", value=authorization_scopes, expected_type=type_hints["authorization_scopes"])
            check_type(argname="argument authorizer", value=authorizer, expected_type=type_hints["authorizer"])
            check_type(argname="argument methods", value=methods, expected_type=type_hints["methods"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration": integration,
            "path": path,
        }
        if authorization_scopes is not None:
            self._values["authorization_scopes"] = authorization_scopes
        if authorizer is not None:
            self._values["authorizer"] = authorizer
        if methods is not None:
            self._values["methods"] = methods

    @builtins.property
    def integration(self) -> HttpRouteIntegration:
        '''(experimental) The integration to be configured on this route.

        :stability: experimental
        '''
        result = self._values.get("integration")
        assert result is not None, "Required property 'integration' is missing"
        return typing.cast(HttpRouteIntegration, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) The path at which all of these routes are configured.

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorization_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The list of OIDC scopes to include in the authorization.

        These scopes will override the default authorization scopes on the gateway.
        Set to [] to remove default scopes

        :default: - uses defaultAuthorizationScopes if configured on the API, otherwise none.

        :stability: experimental
        '''
        result = self._values.get("authorization_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def authorizer(self) -> typing.Optional[IHttpRouteAuthorizer]:
        '''(experimental) Authorizer to be associated to these routes.

        Use NoneAuthorizer to remove the default authorizer for the api

        :default: - uses the default authorizer if one is specified on the HttpApi

        :stability: experimental
        '''
        result = self._values.get("authorizer")
        return typing.cast(typing.Optional[IHttpRouteAuthorizer], result)

    @builtins.property
    def methods(self) -> typing.Optional[typing.List[HttpMethod]]:
        '''(experimental) The HTTP methods to be configured.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("methods")
        return typing.cast(typing.Optional[typing.List[HttpMethod]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddRoutesOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IApiMapping)
class ApiMapping(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.ApiMapping",
):
    '''(experimental) Create a new API mapping for API Gateway API endpoint.

    :stability: experimental
    :resource: AWS::ApiGatewayV2::ApiMapping
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
        
        # api: apigatewayv2_alpha.IApi
        # domain_name: apigatewayv2_alpha.DomainName
        # stage: apigatewayv2_alpha.IStage
        
        api_mapping = apigatewayv2_alpha.ApiMapping(self, "MyApiMapping",
            api=api,
            domain_name=domain_name,
        
            # the properties below are optional
            api_mapping_key="apiMappingKey",
            stage=stage
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api: IApi,
        domain_name: IDomainName,
        api_mapping_key: typing.Optional[builtins.str] = None,
        stage: typing.Optional[IStage] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api: (experimental) The Api to which this mapping is applied.
        :param domain_name: (experimental) custom domain name of the mapping target.
        :param api_mapping_key: (experimental) Api mapping key. The path where this stage should be mapped to on the domain Default: - undefined for the root path mapping.
        :param stage: (experimental) stage for the ApiMapping resource required for WebSocket API defaults to default stage of an HTTP API. Default: - Default stage of the passed API for HTTP API, required for WebSocket API

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbff8656b4f6706b46963d8d04c49514410f8af75cfeb33a4c2fe1a07e9f33ac)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApiMappingProps(
            api=api,
            domain_name=domain_name,
            api_mapping_key=api_mapping_key,
            stage=stage,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromApiMappingAttributes")
    @builtins.classmethod
    def from_api_mapping_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api_mapping_id: builtins.str,
    ) -> IApiMapping:
        '''(experimental) import from API ID.

        :param scope: -
        :param id: -
        :param api_mapping_id: (experimental) The API mapping ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a142e4a61436ea624a748446cb739233abd5326d66a7e1a91f9c88642f61ca94)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = ApiMappingAttributes(api_mapping_id=api_mapping_id)

        return typing.cast(IApiMapping, jsii.sinvoke(cls, "fromApiMappingAttributes", [scope, id, attrs]))

    @builtins.property
    @jsii.member(jsii_name="apiMappingId")
    def api_mapping_id(self) -> builtins.str:
        '''(experimental) ID of the API Mapping.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiMappingId"))

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> IDomainName:
        '''(experimental) API domain name.

        :stability: experimental
        '''
        return typing.cast(IDomainName, jsii.get(self, "domainName"))

    @builtins.property
    @jsii.member(jsii_name="mappingKey")
    def mapping_key(self) -> typing.Optional[builtins.str]:
        '''(experimental) API Mapping key.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mappingKey"))


@jsii.implements(IDomainName)
class DomainName(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.DomainName",
):
    '''(experimental) Custom domain resource for the API.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_certificatemanager as acm
        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
        
        # handler: lambda.Function
        
        
        cert_arn = "arn:aws:acm:us-east-1:111111111111:certificate"
        domain_name = "example.com"
        
        dn = apigwv2.DomainName(self, "DN",
            domain_name=domain_name,
            certificate=acm.Certificate.from_certificate_arn(self, "cert", cert_arn)
        )
        api = apigwv2.HttpApi(self, "HttpProxyProdApi",
            default_integration=HttpLambdaIntegration("DefaultIntegration", handler),
            # https://${dn.domainName}/foo goes to prodApi $default stage
            default_domain_mapping=apigwv2.DomainMappingOptions(
                domain_name=dn,
                mapping_key="foo"
            )
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        mtls: typing.Optional[typing.Union[MTLSConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
        certificate_name: typing.Optional[builtins.str] = None,
        endpoint_type: typing.Optional[EndpointType] = None,
        ownership_certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        security_policy: typing.Optional[SecurityPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_name: (experimental) The custom domain name.
        :param mtls: (experimental) The mutual TLS authentication configuration for a custom domain name. Default: - mTLS is not configured.
        :param certificate: (experimental) The ACM certificate for this domain name. Certificate can be both ACM issued or imported.
        :param certificate_name: (experimental) The user-friendly name of the certificate that will be used by the endpoint for this domain name. Default: - No friendly certificate name
        :param endpoint_type: (experimental) The type of endpoint for this DomainName. Default: EndpointType.REGIONAL
        :param ownership_certificate: (experimental) A public certificate issued by ACM to validate that you own a custom domain. This parameter is required only when you configure mutual TLS authentication and you specify an ACM imported or private CA certificate for ``certificate``. The ownership certificate validates that you have permissions to use the domain name. Default: - only required when configuring mTLS
        :param security_policy: (experimental) The Transport Layer Security (TLS) version + cipher suite for this domain name. Default: SecurityPolicy.TLS_1_2

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9d717e977e1b3688e10b96a28c290636a0c8ffb230b0e32f751c93cfed6ae39)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DomainNameProps(
            domain_name=domain_name,
            mtls=mtls,
            certificate=certificate,
            certificate_name=certificate_name,
            endpoint_type=endpoint_type,
            ownership_certificate=ownership_certificate,
            security_policy=security_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromDomainNameAttributes")
    @builtins.classmethod
    def from_domain_name_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        regional_domain_name: builtins.str,
        regional_hosted_zone_id: builtins.str,
    ) -> IDomainName:
        '''(experimental) Import from attributes.

        :param scope: -
        :param id: -
        :param name: (experimental) domain name string.
        :param regional_domain_name: (experimental) The domain name associated with the regional endpoint for this custom domain name.
        :param regional_hosted_zone_id: (experimental) The region-specific Amazon Route 53 Hosted Zone ID of the regional endpoint.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a75b51d5333f983b1ad28c7723855075bb1accd439fd505ecabd1a569a79bab5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = DomainNameAttributes(
            name=name,
            regional_domain_name=regional_domain_name,
            regional_hosted_zone_id=regional_hosted_zone_id,
        )

        return typing.cast(IDomainName, jsii.sinvoke(cls, "fromDomainNameAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addEndpoint")
    def add_endpoint(
        self,
        *,
        certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
        certificate_name: typing.Optional[builtins.str] = None,
        endpoint_type: typing.Optional[EndpointType] = None,
        ownership_certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        security_policy: typing.Optional[SecurityPolicy] = None,
    ) -> None:
        '''(experimental) Adds an endpoint to a domain name.

        :param certificate: (experimental) The ACM certificate for this domain name. Certificate can be both ACM issued or imported.
        :param certificate_name: (experimental) The user-friendly name of the certificate that will be used by the endpoint for this domain name. Default: - No friendly certificate name
        :param endpoint_type: (experimental) The type of endpoint for this DomainName. Default: EndpointType.REGIONAL
        :param ownership_certificate: (experimental) A public certificate issued by ACM to validate that you own a custom domain. This parameter is required only when you configure mutual TLS authentication and you specify an ACM imported or private CA certificate for ``certificate``. The ownership certificate validates that you have permissions to use the domain name. Default: - only required when configuring mTLS
        :param security_policy: (experimental) The Transport Layer Security (TLS) version + cipher suite for this domain name. Default: SecurityPolicy.TLS_1_2

        :stability: experimental
        '''
        options = EndpointOptions(
            certificate=certificate,
            certificate_name=certificate_name,
            endpoint_type=endpoint_type,
            ownership_certificate=ownership_certificate,
            security_policy=security_policy,
        )

        return typing.cast(None, jsii.invoke(self, "addEndpoint", [options]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The custom domain name.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) The domain name associated with the regional endpoint for this custom domain name.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "regionalDomainName"))

    @builtins.property
    @jsii.member(jsii_name="regionalHostedZoneId")
    def regional_hosted_zone_id(self) -> builtins.str:
        '''(experimental) The region-specific Amazon Route 53 Hosted Zone ID of the regional endpoint.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "regionalHostedZoneId"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.DomainNameProps",
    jsii_struct_bases=[EndpointOptions],
    name_mapping={
        "certificate": "certificate",
        "certificate_name": "certificateName",
        "endpoint_type": "endpointType",
        "ownership_certificate": "ownershipCertificate",
        "security_policy": "securityPolicy",
        "domain_name": "domainName",
        "mtls": "mtls",
    },
)
class DomainNameProps(EndpointOptions):
    def __init__(
        self,
        *,
        certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
        certificate_name: typing.Optional[builtins.str] = None,
        endpoint_type: typing.Optional[EndpointType] = None,
        ownership_certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        security_policy: typing.Optional[SecurityPolicy] = None,
        domain_name: builtins.str,
        mtls: typing.Optional[typing.Union[MTLSConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) properties used for creating the DomainName.

        :param certificate: (experimental) The ACM certificate for this domain name. Certificate can be both ACM issued or imported.
        :param certificate_name: (experimental) The user-friendly name of the certificate that will be used by the endpoint for this domain name. Default: - No friendly certificate name
        :param endpoint_type: (experimental) The type of endpoint for this DomainName. Default: EndpointType.REGIONAL
        :param ownership_certificate: (experimental) A public certificate issued by ACM to validate that you own a custom domain. This parameter is required only when you configure mutual TLS authentication and you specify an ACM imported or private CA certificate for ``certificate``. The ownership certificate validates that you have permissions to use the domain name. Default: - only required when configuring mTLS
        :param security_policy: (experimental) The Transport Layer Security (TLS) version + cipher suite for this domain name. Default: SecurityPolicy.TLS_1_2
        :param domain_name: (experimental) The custom domain name.
        :param mtls: (experimental) The mutual TLS authentication configuration for a custom domain name. Default: - mTLS is not configured.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_certificatemanager as acm
            from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
            
            # handler: lambda.Function
            
            
            cert_arn = "arn:aws:acm:us-east-1:111111111111:certificate"
            domain_name = "example.com"
            
            dn = apigwv2.DomainName(self, "DN",
                domain_name=domain_name,
                certificate=acm.Certificate.from_certificate_arn(self, "cert", cert_arn)
            )
            api = apigwv2.HttpApi(self, "HttpProxyProdApi",
                default_integration=HttpLambdaIntegration("DefaultIntegration", handler),
                # https://${dn.domainName}/foo goes to prodApi $default stage
                default_domain_mapping=apigwv2.DomainMappingOptions(
                    domain_name=dn,
                    mapping_key="foo"
                )
            )
        '''
        if isinstance(mtls, dict):
            mtls = MTLSConfig(**mtls)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__698fe2808c79855db0ec402620f39e09a615424a13b6af162379044207a388e5)
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument certificate_name", value=certificate_name, expected_type=type_hints["certificate_name"])
            check_type(argname="argument endpoint_type", value=endpoint_type, expected_type=type_hints["endpoint_type"])
            check_type(argname="argument ownership_certificate", value=ownership_certificate, expected_type=type_hints["ownership_certificate"])
            check_type(argname="argument security_policy", value=security_policy, expected_type=type_hints["security_policy"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument mtls", value=mtls, expected_type=type_hints["mtls"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificate": certificate,
            "domain_name": domain_name,
        }
        if certificate_name is not None:
            self._values["certificate_name"] = certificate_name
        if endpoint_type is not None:
            self._values["endpoint_type"] = endpoint_type
        if ownership_certificate is not None:
            self._values["ownership_certificate"] = ownership_certificate
        if security_policy is not None:
            self._values["security_policy"] = security_policy
        if mtls is not None:
            self._values["mtls"] = mtls

    @builtins.property
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''(experimental) The ACM certificate for this domain name.

        Certificate can be both ACM issued or imported.

        :stability: experimental
        '''
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, result)

    @builtins.property
    def certificate_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The user-friendly name of the certificate that will be used by the endpoint for this domain name.

        :default: - No friendly certificate name

        :stability: experimental
        '''
        result = self._values.get("certificate_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint_type(self) -> typing.Optional[EndpointType]:
        '''(experimental) The type of endpoint for this DomainName.

        :default: EndpointType.REGIONAL

        :stability: experimental
        '''
        result = self._values.get("endpoint_type")
        return typing.cast(typing.Optional[EndpointType], result)

    @builtins.property
    def ownership_certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''(experimental) A public certificate issued by ACM to validate that you own a custom domain.

        This parameter is required
        only when you configure mutual TLS authentication and you specify an ACM imported or private CA certificate
        for ``certificate``. The ownership certificate validates that you have permissions to use the domain name.

        :default: - only required when configuring mTLS

        :stability: experimental
        '''
        result = self._values.get("ownership_certificate")
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def security_policy(self) -> typing.Optional[SecurityPolicy]:
        '''(experimental) The Transport Layer Security (TLS) version + cipher suite for this domain name.

        :default: SecurityPolicy.TLS_1_2

        :stability: experimental
        '''
        result = self._values.get("security_policy")
        return typing.cast(typing.Optional[SecurityPolicy], result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''(experimental) The custom domain name.

        :stability: experimental
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mtls(self) -> typing.Optional[MTLSConfig]:
        '''(experimental) The mutual TLS authentication configuration for a custom domain name.

        :default: - mTLS is not configured.

        :stability: experimental
        '''
        result = self._values.get("mtls")
        return typing.cast(typing.Optional[MTLSConfig], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainNameProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IHttpApi, IApi)
class HttpApi(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpApi",
):
    '''(experimental) Create a new API Gateway HTTP API endpoint.

    :stability: experimental
    :resource: AWS::ApiGatewayV2::Api
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
        
        # books_default_fn: lambda.Function
        
        books_integration = HttpLambdaIntegration("BooksIntegration", books_default_fn)
        
        http_api = apigwv2.HttpApi(self, "HttpApi")
        
        http_api.add_routes(
            path="/books",
            methods=[apigwv2.HttpMethod.GET],
            integration=books_integration
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api_name: typing.Optional[builtins.str] = None,
        cors_preflight: typing.Optional[typing.Union[CorsPreflightOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        create_default_stage: typing.Optional[builtins.bool] = None,
        default_authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_authorizer: typing.Optional[IHttpRouteAuthorizer] = None,
        default_domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        default_integration: typing.Optional[HttpRouteIntegration] = None,
        description: typing.Optional[builtins.str] = None,
        disable_execute_api_endpoint: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api_name: (experimental) Name for the HTTP API resource. Default: - id of the HttpApi construct.
        :param cors_preflight: (experimental) Specifies a CORS configuration for an API. Default: - CORS disabled.
        :param create_default_stage: (experimental) Whether a default stage and deployment should be automatically created. Default: true
        :param default_authorization_scopes: (experimental) Default OIDC scopes attached to all routes in the gateway, unless explicitly configured on the route. Default: - no default authorization scopes
        :param default_authorizer: (experimental) Default Authorizer to applied to all routes in the gateway. Default: - No authorizer
        :param default_domain_mapping: (experimental) Configure a custom domain with the API mapping resource to the HTTP API. Default: - no default domain mapping configured. meaningless if ``createDefaultStage`` is ``false``.
        :param default_integration: (experimental) An integration that will be configured on the catch-all route ($default). Default: - none
        :param description: (experimental) The description of the API. Default: - none
        :param disable_execute_api_endpoint: (experimental) Specifies whether clients can invoke your API using the default endpoint. By default, clients can invoke your API with the default ``https://{api_id}.execute-api.{region}.amazonaws.com`` endpoint. Enable this if you would like clients to use your custom domain name. Default: false execute-api endpoint enabled.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5003409414773984b85252451580f75369de42c80978f161fece7261c553c54)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = HttpApiProps(
            api_name=api_name,
            cors_preflight=cors_preflight,
            create_default_stage=create_default_stage,
            default_authorization_scopes=default_authorization_scopes,
            default_authorizer=default_authorizer,
            default_domain_mapping=default_domain_mapping,
            default_integration=default_integration,
            description=description,
            disable_execute_api_endpoint=disable_execute_api_endpoint,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromHttpApiAttributes")
    @builtins.classmethod
    def from_http_api_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        http_api_id: builtins.str,
        api_endpoint: typing.Optional[builtins.str] = None,
    ) -> IHttpApi:
        '''(experimental) Import an existing HTTP API into this CDK app.

        :param scope: -
        :param id: -
        :param http_api_id: (experimental) The identifier of the HttpApi.
        :param api_endpoint: (experimental) The endpoint URL of the HttpApi. Default: - throws an error if apiEndpoint is accessed.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecd315f15fe552c95da2ac31778a118bb3415d560941e8d18e9c71e631481225)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = HttpApiAttributes(http_api_id=http_api_id, api_endpoint=api_endpoint)

        return typing.cast(IHttpApi, jsii.sinvoke(cls, "fromHttpApiAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addRoutes")
    def add_routes(
        self,
        *,
        path: builtins.str,
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        authorizer: typing.Optional[IHttpRouteAuthorizer] = None,
        methods: typing.Optional[typing.Sequence[HttpMethod]] = None,
        integration: HttpRouteIntegration,
    ) -> typing.List["HttpRoute"]:
        '''(experimental) Add multiple routes that uses the same configuration.

        The routes all go to the same path, but for different
        methods.

        :param path: (experimental) The path at which all of these routes are configured.
        :param authorization_scopes: (experimental) The list of OIDC scopes to include in the authorization. These scopes will override the default authorization scopes on the gateway. Set to [] to remove default scopes Default: - uses defaultAuthorizationScopes if configured on the API, otherwise none.
        :param authorizer: (experimental) Authorizer to be associated to these routes. Use NoneAuthorizer to remove the default authorizer for the api Default: - uses the default authorizer if one is specified on the HttpApi
        :param methods: (experimental) The HTTP methods to be configured. Default: HttpMethod.ANY
        :param integration: (experimental) The integration to be configured on this route.

        :stability: experimental
        '''
        options = AddRoutesOptions(
            path=path,
            authorization_scopes=authorization_scopes,
            authorizer=authorizer,
            methods=methods,
            integration=integration,
        )

        return typing.cast(typing.List["HttpRoute"], jsii.invoke(self, "addRoutes", [options]))

    @jsii.member(jsii_name="addStage")
    def add_stage(
        self,
        id: builtins.str,
        *,
        stage_name: typing.Optional[builtins.str] = None,
        auto_deploy: typing.Optional[builtins.bool] = None,
        domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "HttpStage":
        '''(experimental) Add a new stage.

        :param id: -
        :param stage_name: (experimental) The name of the stage. See ``StageName`` class for more details. Default: '$default' the default stage of the API. This stage will have the URL at the root of the API endpoint.
        :param auto_deploy: (experimental) Whether updates to an API automatically trigger a new deployment. Default: false
        :param domain_mapping: (experimental) The options for custom domain and api mapping. Default: - no custom domain and api mapping configuration
        :param throttle: (experimental) Throttle settings for the routes of this stage. Default: - no throttling configuration

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bab5e6089f6e913d418934d66da25f8a39159ad3bd9f9f115cbcde831da78e0)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = HttpStageOptions(
            stage_name=stage_name,
            auto_deploy=auto_deploy,
            domain_mapping=domain_mapping,
            throttle=throttle,
        )

        return typing.cast("HttpStage", jsii.invoke(self, "addStage", [id, options]))

    @jsii.member(jsii_name="addVpcLink")
    def add_vpc_link(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_link_name: typing.Optional[builtins.str] = None,
    ) -> VpcLink:
        '''(experimental) Add a new VpcLink.

        :param vpc: (experimental) The VPC in which the private resources reside.
        :param security_groups: (experimental) A list of security groups for the VPC link. Default: - no security groups. Use ``addSecurityGroups`` to add security groups
        :param subnets: (experimental) A list of subnets for the VPC link. Default: - private subnets of the provided VPC. Use ``addSubnets`` to add more subnets
        :param vpc_link_name: (experimental) The name used to label and identify the VPC link. Default: - automatically generated name

        :stability: experimental
        '''
        options = VpcLinkProps(
            vpc=vpc,
            security_groups=security_groups,
            subnets=subnets,
            vpc_link_name=vpc_link_name,
        )

        return typing.cast(VpcLink, jsii.invoke(self, "addVpcLink", [options]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this Api Gateway.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7709e3cbcd45c7d4a9b816ad94388873b7fd0558ca6fdcb427f2d5ca6e8df6a)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricClientError")
    def metric_client_error(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the number of client-side errors captured in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricClientError", [props]))

    @jsii.member(jsii_name="metricCount")
    def metric_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the total number API requests in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricCount", [props]))

    @jsii.member(jsii_name="metricDataProcessed")
    def metric_data_processed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the amount of data processed in bytes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricDataProcessed", [props]))

    @jsii.member(jsii_name="metricIntegrationLatency")
    def metric_integration_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the time between when API Gateway relays a request to the backend and when it receives a response from the backend.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricIntegrationLatency", [props]))

    @jsii.member(jsii_name="metricLatency")
    def metric_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) The time between when API Gateway receives a request from a client and when it returns a response to the client.

        The latency includes the integration latency and other API Gateway overhead.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricLatency", [props]))

    @jsii.member(jsii_name="metricServerError")
    def metric_server_error(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the number of server-side errors captured in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricServerError", [props]))

    @builtins.property
    @jsii.member(jsii_name="apiEndpoint")
    def api_endpoint(self) -> builtins.str:
        '''(experimental) Get the default endpoint for this API.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''(experimental) The identifier of this API Gateway API.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @builtins.property
    @jsii.member(jsii_name="httpApiId")
    def http_api_id(self) -> builtins.str:
        '''(experimental) The identifier of this API Gateway HTTP API.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "httpApiId"))

    @builtins.property
    @jsii.member(jsii_name="defaultStage")
    def default_stage(self) -> typing.Optional["IHttpStage"]:
        '''(experimental) The default stage of this API.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["IHttpStage"], jsii.get(self, "defaultStage"))

    @builtins.property
    @jsii.member(jsii_name="disableExecuteApiEndpoint")
    def disable_execute_api_endpoint(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies whether clients can invoke this HTTP API by using the default execute-api endpoint.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "disableExecuteApiEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="httpApiName")
    def http_api_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A human friendly name for this HTTP API.

        Note that this is different from ``httpApiId``.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpApiName"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Get the URL to the default stage of this API.

        Returns ``undefined`` if ``createDefaultStage`` is unset.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))


@jsii.implements(IHttpAuthorizer)
class HttpAuthorizer(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpAuthorizer",
):
    '''(experimental) An authorizer for Http Apis.

    :stability: experimental
    :resource: AWS::ApiGatewayV2::Authorizer
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
        import aws_cdk as cdk
        
        # http_api: apigatewayv2_alpha.HttpApi
        
        http_authorizer = apigatewayv2_alpha.HttpAuthorizer(self, "MyHttpAuthorizer",
            http_api=http_api,
            identity_source=["identitySource"],
            type=apigatewayv2_alpha.HttpAuthorizerType.IAM,
        
            # the properties below are optional
            authorizer_name="authorizerName",
            authorizer_uri="authorizerUri",
            enable_simple_responses=False,
            jwt_audience=["jwtAudience"],
            jwt_issuer="jwtIssuer",
            payload_format_version=apigatewayv2_alpha.AuthorizerPayloadVersion.VERSION_1_0,
            results_cache_ttl=cdk.Duration.minutes(30)
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        http_api: IHttpApi,
        identity_source: typing.Sequence[builtins.str],
        type: HttpAuthorizerType,
        authorizer_name: typing.Optional[builtins.str] = None,
        authorizer_uri: typing.Optional[builtins.str] = None,
        enable_simple_responses: typing.Optional[builtins.bool] = None,
        jwt_audience: typing.Optional[typing.Sequence[builtins.str]] = None,
        jwt_issuer: typing.Optional[builtins.str] = None,
        payload_format_version: typing.Optional[AuthorizerPayloadVersion] = None,
        results_cache_ttl: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param http_api: (experimental) HTTP Api to attach the authorizer to.
        :param identity_source: (experimental) The identity source for which authorization is requested.
        :param type: (experimental) The type of authorizer.
        :param authorizer_name: (experimental) Name of the authorizer. Default: - id of the HttpAuthorizer construct.
        :param authorizer_uri: (experimental) The authorizer's Uniform Resource Identifier (URI). For REQUEST authorizers, this must be a well-formed Lambda function URI. Default: - required for Request authorizer types
        :param enable_simple_responses: (experimental) Specifies whether a Lambda authorizer returns a response in a simple format. If enabled, the Lambda authorizer can return a boolean value instead of an IAM policy. Default: - The lambda authorizer must return an IAM policy as its response
        :param jwt_audience: (experimental) A list of the intended recipients of the JWT. A valid JWT must provide an aud that matches at least one entry in this list. Default: - required for JWT authorizer typess.
        :param jwt_issuer: (experimental) The base domain of the identity provider that issues JWT. Default: - required for JWT authorizer types.
        :param payload_format_version: (experimental) Specifies the format of the payload sent to an HTTP API Lambda authorizer. Default: AuthorizerPayloadVersion.VERSION_2_0 if the authorizer type is HttpAuthorizerType.LAMBDA
        :param results_cache_ttl: (experimental) How long APIGateway should cache the results. Max 1 hour. Default: - API Gateway will not cache authorizer responses

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03f7fb4792b9161dda177d8df2f5bc58091a4f546c4ca11ee18afaa4e0bf5e28)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = HttpAuthorizerProps(
            http_api=http_api,
            identity_source=identity_source,
            type=type,
            authorizer_name=authorizer_name,
            authorizer_uri=authorizer_uri,
            enable_simple_responses=enable_simple_responses,
            jwt_audience=jwt_audience,
            jwt_issuer=jwt_issuer,
            payload_format_version=payload_format_version,
            results_cache_ttl=results_cache_ttl,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromHttpAuthorizerAttributes")
    @builtins.classmethod
    def from_http_authorizer_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        authorizer_id: builtins.str,
        authorizer_type: builtins.str,
    ) -> IHttpRouteAuthorizer:
        '''(experimental) Import an existing HTTP Authorizer into this CDK app.

        :param scope: -
        :param id: -
        :param authorizer_id: (experimental) Id of the Authorizer.
        :param authorizer_type: (experimental) Type of authorizer. Possible values are: - JWT - JSON Web Token Authorizer - CUSTOM - Lambda Authorizer - NONE - No Authorization

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efb4a2f65822f686a6ffa7ada308b84e89325054661df552cb9bc6286414ff5b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = HttpAuthorizerAttributes(
            authorizer_id=authorizer_id, authorizer_type=authorizer_type
        )

        return typing.cast(IHttpRouteAuthorizer, jsii.sinvoke(cls, "fromHttpAuthorizerAttributes", [scope, id, attrs]))

    @builtins.property
    @jsii.member(jsii_name="authorizerId")
    def authorizer_id(self) -> builtins.str:
        '''(experimental) Id of the Authorizer.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "authorizerId"))


@jsii.implements(IHttpRouteAuthorizer)
class HttpNoneAuthorizer(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpNoneAuthorizer",
):
    '''(experimental) Explicitly configure no authorizers on specific HTTP API routes.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpJwtAuthorizer
        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration
        
        
        issuer = "https://test.us.auth0.com"
        authorizer = HttpJwtAuthorizer("DefaultAuthorizer", issuer,
            jwt_audience=["3131231"]
        )
        
        api = apigwv2.HttpApi(self, "HttpApi",
            default_authorizer=authorizer,
            default_authorization_scopes=["read:books"]
        )
        
        api.add_routes(
            integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.example.com"),
            path="/books",
            methods=[apigwv2.HttpMethod.GET]
        )
        
        api.add_routes(
            integration=HttpUrlIntegration("BooksIdIntegration", "https://get-books-proxy.example.com"),
            path="/books/{id}",
            methods=[apigwv2.HttpMethod.GET]
        )
        
        api.add_routes(
            integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.example.com"),
            path="/books",
            methods=[apigwv2.HttpMethod.POST],
            authorization_scopes=["write:books"]
        )
        
        api.add_routes(
            integration=HttpUrlIntegration("LoginIntegration", "https://get-books-proxy.example.com"),
            path="/login",
            methods=[apigwv2.HttpMethod.POST],
            authorizer=apigwv2.HttpNoneAuthorizer()
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: "IHttpRoute",
        scope: _constructs_77d1e7e8.Construct,
    ) -> HttpRouteAuthorizerConfig:
        '''(experimental) Bind this authorizer to a specified Http route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        _ = HttpRouteAuthorizerBindOptions(route=route, scope=scope)

        return typing.cast(HttpRouteAuthorizerConfig, jsii.invoke(self, "bind", [_]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpStageAttributes",
    jsii_struct_bases=[StageAttributes],
    name_mapping={"stage_name": "stageName", "api": "api"},
)
class HttpStageAttributes(StageAttributes):
    def __init__(self, *, stage_name: builtins.str, api: IHttpApi) -> None:
        '''(experimental) The attributes used to import existing HttpStage.

        :param stage_name: (experimental) The name of the stage.
        :param api: (experimental) The API to which this stage is associated.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            
            # http_api: apigatewayv2_alpha.HttpApi
            
            http_stage_attributes = apigatewayv2_alpha.HttpStageAttributes(
                api=http_api,
                stage_name="stageName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68b934e47d5c501cf4c24923fe5b089fdb197a5624c649d8f83e58305cd890d5)
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument api", value=api, expected_type=type_hints["api"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stage_name": stage_name,
            "api": api,
        }

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''(experimental) The name of the stage.

        :stability: experimental
        '''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api(self) -> IHttpApi:
        '''(experimental) The API to which this stage is associated.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(IHttpApi, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpStageAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpStageOptions",
    jsii_struct_bases=[StageOptions],
    name_mapping={
        "auto_deploy": "autoDeploy",
        "domain_mapping": "domainMapping",
        "throttle": "throttle",
        "stage_name": "stageName",
    },
)
class HttpStageOptions(StageOptions):
    def __init__(
        self,
        *,
        auto_deploy: typing.Optional[builtins.bool] = None,
        domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) The options to create a new Stage for an HTTP API.

        :param auto_deploy: (experimental) Whether updates to an API automatically trigger a new deployment. Default: false
        :param domain_mapping: (experimental) The options for custom domain and api mapping. Default: - no custom domain and api mapping configuration
        :param throttle: (experimental) Throttle settings for the routes of this stage. Default: - no throttling configuration
        :param stage_name: (experimental) The name of the stage. See ``StageName`` class for more details. Default: '$default' the default stage of the API. This stage will have the URL at the root of the API endpoint.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # api: apigwv2.HttpApi
            # dn: apigwv2.DomainName
            
            
            api.add_stage("beta",
                stage_name="beta",
                auto_deploy=True,
                # https://${dn.domainName}/bar goes to the beta stage
                domain_mapping=apigwv2.DomainMappingOptions(
                    domain_name=dn,
                    mapping_key="bar"
                )
            )
        '''
        if isinstance(domain_mapping, dict):
            domain_mapping = DomainMappingOptions(**domain_mapping)
        if isinstance(throttle, dict):
            throttle = ThrottleSettings(**throttle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e64c35e906d5449f8f7b3901603109565a527cbb27318f310243b054419c4a7)
            check_type(argname="argument auto_deploy", value=auto_deploy, expected_type=type_hints["auto_deploy"])
            check_type(argname="argument domain_mapping", value=domain_mapping, expected_type=type_hints["domain_mapping"])
            check_type(argname="argument throttle", value=throttle, expected_type=type_hints["throttle"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auto_deploy is not None:
            self._values["auto_deploy"] = auto_deploy
        if domain_mapping is not None:
            self._values["domain_mapping"] = domain_mapping
        if throttle is not None:
            self._values["throttle"] = throttle
        if stage_name is not None:
            self._values["stage_name"] = stage_name

    @builtins.property
    def auto_deploy(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether updates to an API automatically trigger a new deployment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("auto_deploy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain_mapping(self) -> typing.Optional[DomainMappingOptions]:
        '''(experimental) The options for custom domain and api mapping.

        :default: - no custom domain and api mapping configuration

        :stability: experimental
        '''
        result = self._values.get("domain_mapping")
        return typing.cast(typing.Optional[DomainMappingOptions], result)

    @builtins.property
    def throttle(self) -> typing.Optional[ThrottleSettings]:
        '''(experimental) Throttle settings for the routes of this stage.

        :default: - no throttling configuration

        :stability: experimental
        '''
        result = self._values.get("throttle")
        return typing.cast(typing.Optional[ThrottleSettings], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the stage.

        See ``StageName`` class for more details.

        :default: '$default' the default stage of the API. This stage will have the URL at the root of the API endpoint.

        :stability: experimental
        '''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpStageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpStageProps",
    jsii_struct_bases=[HttpStageOptions],
    name_mapping={
        "auto_deploy": "autoDeploy",
        "domain_mapping": "domainMapping",
        "throttle": "throttle",
        "stage_name": "stageName",
        "http_api": "httpApi",
    },
)
class HttpStageProps(HttpStageOptions):
    def __init__(
        self,
        *,
        auto_deploy: typing.Optional[builtins.bool] = None,
        domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        stage_name: typing.Optional[builtins.str] = None,
        http_api: IHttpApi,
    ) -> None:
        '''(experimental) Properties to initialize an instance of ``HttpStage``.

        :param auto_deploy: (experimental) Whether updates to an API automatically trigger a new deployment. Default: false
        :param domain_mapping: (experimental) The options for custom domain and api mapping. Default: - no custom domain and api mapping configuration
        :param throttle: (experimental) Throttle settings for the routes of this stage. Default: - no throttling configuration
        :param stage_name: (experimental) The name of the stage. See ``StageName`` class for more details. Default: '$default' the default stage of the API. This stage will have the URL at the root of the API endpoint.
        :param http_api: (experimental) The HTTP API to which this stage is associated.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # api: apigwv2.HttpApi
            
            
            apigwv2.HttpStage(self, "Stage",
                http_api=api,
                stage_name="beta"
            )
        '''
        if isinstance(domain_mapping, dict):
            domain_mapping = DomainMappingOptions(**domain_mapping)
        if isinstance(throttle, dict):
            throttle = ThrottleSettings(**throttle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__925560a3ec43c8b350658e7729b7c093c0eb2dc51b442b9b5877c46ec328fbb4)
            check_type(argname="argument auto_deploy", value=auto_deploy, expected_type=type_hints["auto_deploy"])
            check_type(argname="argument domain_mapping", value=domain_mapping, expected_type=type_hints["domain_mapping"])
            check_type(argname="argument throttle", value=throttle, expected_type=type_hints["throttle"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument http_api", value=http_api, expected_type=type_hints["http_api"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "http_api": http_api,
        }
        if auto_deploy is not None:
            self._values["auto_deploy"] = auto_deploy
        if domain_mapping is not None:
            self._values["domain_mapping"] = domain_mapping
        if throttle is not None:
            self._values["throttle"] = throttle
        if stage_name is not None:
            self._values["stage_name"] = stage_name

    @builtins.property
    def auto_deploy(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether updates to an API automatically trigger a new deployment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("auto_deploy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain_mapping(self) -> typing.Optional[DomainMappingOptions]:
        '''(experimental) The options for custom domain and api mapping.

        :default: - no custom domain and api mapping configuration

        :stability: experimental
        '''
        result = self._values.get("domain_mapping")
        return typing.cast(typing.Optional[DomainMappingOptions], result)

    @builtins.property
    def throttle(self) -> typing.Optional[ThrottleSettings]:
        '''(experimental) Throttle settings for the routes of this stage.

        :default: - no throttling configuration

        :stability: experimental
        '''
        result = self._values.get("throttle")
        return typing.cast(typing.Optional[ThrottleSettings], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the stage.

        See ``StageName`` class for more details.

        :default: '$default' the default stage of the API. This stage will have the URL at the root of the API endpoint.

        :stability: experimental
        '''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_api(self) -> IHttpApi:
        '''(experimental) The HTTP API to which this stage is associated.

        :stability: experimental
        '''
        result = self._values.get("http_api")
        assert result is not None, "Required property 'http_api' is missing"
        return typing.cast(IHttpApi, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IHttpIntegration")
class IHttpIntegration(IIntegration, typing_extensions.Protocol):
    '''(experimental) Represents an Integration for an HTTP API.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="httpApi")
    def http_api(self) -> IHttpApi:
        '''(experimental) The HTTP API associated with this integration.

        :stability: experimental
        '''
        ...


class _IHttpIntegrationProxy(
    jsii.proxy_for(IIntegration), # type: ignore[misc]
):
    '''(experimental) Represents an Integration for an HTTP API.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IHttpIntegration"

    @builtins.property
    @jsii.member(jsii_name="httpApi")
    def http_api(self) -> IHttpApi:
        '''(experimental) The HTTP API associated with this integration.

        :stability: experimental
        '''
        return typing.cast(IHttpApi, jsii.get(self, "httpApi"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IHttpIntegration).__jsii_proxy_class__ = lambda : _IHttpIntegrationProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IHttpRoute")
class IHttpRoute(IRoute, typing_extensions.Protocol):
    '''(experimental) Represents a Route for an HTTP API.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="httpApi")
    def http_api(self) -> IHttpApi:
        '''(experimental) The HTTP API associated with this route.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="routeArn")
    def route_arn(self) -> builtins.str:
        '''(experimental) Returns the arn of the route.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> typing.Optional[builtins.str]:
        '''(experimental) Returns the path component of this HTTP route, ``undefined`` if the path is the catch-all route.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *,
        http_methods: typing.Optional[typing.Sequence[HttpMethod]] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant access to invoke the route.

        This method requires that the authorizer of the route is undefined or is
        an ``HttpIamAuthorizer``.

        :param grantee: -
        :param http_methods: (experimental) The HTTP methods to allow. Default: - the HttpMethod of the route

        :stability: experimental
        '''
        ...


class _IHttpRouteProxy(
    jsii.proxy_for(IRoute), # type: ignore[misc]
):
    '''(experimental) Represents a Route for an HTTP API.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IHttpRoute"

    @builtins.property
    @jsii.member(jsii_name="httpApi")
    def http_api(self) -> IHttpApi:
        '''(experimental) The HTTP API associated with this route.

        :stability: experimental
        '''
        return typing.cast(IHttpApi, jsii.get(self, "httpApi"))

    @builtins.property
    @jsii.member(jsii_name="routeArn")
    def route_arn(self) -> builtins.str:
        '''(experimental) Returns the arn of the route.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "routeArn"))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> typing.Optional[builtins.str]:
        '''(experimental) Returns the path component of this HTTP route, ``undefined`` if the path is the catch-all route.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "path"))

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *,
        http_methods: typing.Optional[typing.Sequence[HttpMethod]] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant access to invoke the route.

        This method requires that the authorizer of the route is undefined or is
        an ``HttpIamAuthorizer``.

        :param grantee: -
        :param http_methods: (experimental) The HTTP methods to allow. Default: - the HttpMethod of the route

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e68d78a6fdd2cf02aa0a9db3e16ddc620002125429503856eb2206ca6638a462)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        options = GrantInvokeOptions(http_methods=http_methods)

        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvoke", [grantee, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IHttpRoute).__jsii_proxy_class__ = lambda : _IHttpRouteProxy


@jsii.interface(jsii_type="@aws-cdk/aws-apigatewayv2-alpha.IHttpStage")
class IHttpStage(IStage, typing_extensions.Protocol):
    '''(experimental) Represents the HttpStage.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="api")
    def api(self) -> IHttpApi:
        '''(experimental) The API this stage is associated to.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="domainUrl")
    def domain_url(self) -> builtins.str:
        '''(experimental) The custom domain URL to this stage.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricClientError")
    def metric_client_error(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the number of client-side errors captured in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricCount")
    def metric_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the total number API requests in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - SampleCount over 5 minutes

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricDataProcessed")
    def metric_data_processed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the amount of data processed in bytes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricIntegrationLatency")
    def metric_integration_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the time between when API Gateway relays a request to the backend and when it receives a response from the backend.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - no statistic

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricLatency")
    def metric_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) The time between when API Gateway receives a request from a client and when it returns a response to the client.

        The latency includes the integration latency and other API Gateway overhead.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - no statistic

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricServerError")
    def metric_server_error(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the number of server-side errors captured in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes

        :stability: experimental
        '''
        ...


class _IHttpStageProxy(
    jsii.proxy_for(IStage), # type: ignore[misc]
):
    '''(experimental) Represents the HttpStage.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-apigatewayv2-alpha.IHttpStage"

    @builtins.property
    @jsii.member(jsii_name="api")
    def api(self) -> IHttpApi:
        '''(experimental) The API this stage is associated to.

        :stability: experimental
        '''
        return typing.cast(IHttpApi, jsii.get(self, "api"))

    @builtins.property
    @jsii.member(jsii_name="domainUrl")
    def domain_url(self) -> builtins.str:
        '''(experimental) The custom domain URL to this stage.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainUrl"))

    @jsii.member(jsii_name="metricClientError")
    def metric_client_error(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the number of client-side errors captured in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricClientError", [props]))

    @jsii.member(jsii_name="metricCount")
    def metric_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the total number API requests in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - SampleCount over 5 minutes

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricCount", [props]))

    @jsii.member(jsii_name="metricDataProcessed")
    def metric_data_processed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the amount of data processed in bytes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricDataProcessed", [props]))

    @jsii.member(jsii_name="metricIntegrationLatency")
    def metric_integration_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the time between when API Gateway relays a request to the backend and when it receives a response from the backend.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - no statistic

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricIntegrationLatency", [props]))

    @jsii.member(jsii_name="metricLatency")
    def metric_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) The time between when API Gateway receives a request from a client and when it returns a response to the client.

        The latency includes the integration latency and other API Gateway overhead.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - no statistic

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricLatency", [props]))

    @jsii.member(jsii_name="metricServerError")
    def metric_server_error(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the number of server-side errors captured in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricServerError", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IHttpStage).__jsii_proxy_class__ = lambda : _IHttpStageProxy


@jsii.implements(IHttpIntegration)
class HttpIntegration(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpIntegration",
):
    '''(experimental) The integration for an API route.

    :stability: experimental
    :resource: AWS::ApiGatewayV2::Integration
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
        
        # http_api: apigatewayv2_alpha.HttpApi
        # integration_credentials: apigatewayv2_alpha.IntegrationCredentials
        # parameter_mapping: apigatewayv2_alpha.ParameterMapping
        # payload_format_version: apigatewayv2_alpha.PayloadFormatVersion
        
        http_integration = apigatewayv2_alpha.HttpIntegration(self, "MyHttpIntegration",
            http_api=http_api,
            integration_type=apigatewayv2_alpha.HttpIntegrationType.HTTP_PROXY,
        
            # the properties below are optional
            connection_id="connectionId",
            connection_type=apigatewayv2_alpha.HttpConnectionType.VPC_LINK,
            credentials=integration_credentials,
            integration_subtype=apigatewayv2_alpha.HttpIntegrationSubtype.EVENTBRIDGE_PUT_EVENTS,
            integration_uri="integrationUri",
            method=apigatewayv2_alpha.HttpMethod.ANY,
            parameter_mapping=parameter_mapping,
            payload_format_version=payload_format_version,
            secure_server_name="secureServerName"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        http_api: IHttpApi,
        integration_type: HttpIntegrationType,
        connection_id: typing.Optional[builtins.str] = None,
        connection_type: typing.Optional[HttpConnectionType] = None,
        credentials: typing.Optional[IntegrationCredentials] = None,
        integration_subtype: typing.Optional[HttpIntegrationSubtype] = None,
        integration_uri: typing.Optional[builtins.str] = None,
        method: typing.Optional[HttpMethod] = None,
        parameter_mapping: typing.Optional[ParameterMapping] = None,
        payload_format_version: typing.Optional[PayloadFormatVersion] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param http_api: (experimental) The HTTP API to which this integration should be bound.
        :param integration_type: (experimental) Integration type.
        :param connection_id: (experimental) The ID of the VPC link for a private integration. Supported only for HTTP APIs. Default: - undefined
        :param connection_type: (experimental) The type of the network connection to the integration endpoint. Default: HttpConnectionType.INTERNET
        :param credentials: (experimental) The credentials with which to invoke the integration. Default: - no credentials, use resource-based permissions on supported AWS services
        :param integration_subtype: (experimental) Integration subtype. Used for AWS Service integrations, specifies the target of the integration. Default: - none, required if no ``integrationUri`` is defined.
        :param integration_uri: (experimental) Integration URI. This will be the function ARN in the case of ``HttpIntegrationType.AWS_PROXY``, or HTTP URL in the case of ``HttpIntegrationType.HTTP_PROXY``. Default: - none, required if no ``integrationSubtype`` is defined.
        :param method: (experimental) The HTTP method to use when calling the underlying HTTP proxy. Default: - none. required if the integration type is ``HttpIntegrationType.HTTP_PROXY``.
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param payload_format_version: (experimental) The version of the payload format. Default: - defaults to latest in the case of HttpIntegrationType.AWS_PROXY`, irrelevant otherwise.
        :param secure_server_name: (experimental) Specifies the TLS configuration for a private integration. Default: undefined private integration traffic will use HTTP protocol

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3de74d25b3d7d1e17696a2da7bd0666d13d0467eed87993389dc688e2ffcf281)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = HttpIntegrationProps(
            http_api=http_api,
            integration_type=integration_type,
            connection_id=connection_id,
            connection_type=connection_type,
            credentials=credentials,
            integration_subtype=integration_subtype,
            integration_uri=integration_uri,
            method=method,
            parameter_mapping=parameter_mapping,
            payload_format_version=payload_format_version,
            secure_server_name=secure_server_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="httpApi")
    def http_api(self) -> IHttpApi:
        '''(experimental) The HTTP API associated with this integration.

        :stability: experimental
        '''
        return typing.cast(IHttpApi, jsii.get(self, "httpApi"))

    @builtins.property
    @jsii.member(jsii_name="integrationId")
    def integration_id(self) -> builtins.str:
        '''(experimental) Id of the integration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "integrationId"))


@jsii.implements(IHttpRoute)
class HttpRoute(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpRoute",
):
    '''(experimental) Route class that creates the Route for API Gateway HTTP API.

    :stability: experimental
    :resource: AWS::ApiGatewayV2::Route
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
        
        # http_api: apigatewayv2_alpha.HttpApi
        # http_route_authorizer: apigatewayv2_alpha.IHttpRouteAuthorizer
        # http_route_integration: apigatewayv2_alpha.HttpRouteIntegration
        # http_route_key: apigatewayv2_alpha.HttpRouteKey
        
        http_route = apigatewayv2_alpha.HttpRoute(self, "MyHttpRoute",
            http_api=http_api,
            integration=http_route_integration,
            route_key=http_route_key,
        
            # the properties below are optional
            authorization_scopes=["authorizationScopes"],
            authorizer=http_route_authorizer
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        http_api: IHttpApi,
        route_key: HttpRouteKey,
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        authorizer: typing.Optional[IHttpRouteAuthorizer] = None,
        integration: HttpRouteIntegration,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param http_api: (experimental) the API the route is associated with.
        :param route_key: (experimental) The key to this route. This is a combination of an HTTP method and an HTTP path.
        :param authorization_scopes: (experimental) The list of OIDC scopes to include in the authorization. These scopes will be merged with the scopes from the attached authorizer Default: - no additional authorization scopes
        :param authorizer: (experimental) Authorizer for a WebSocket API or an HTTP API. Default: - No authorizer
        :param integration: (experimental) The integration to be configured on this route.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d456143a18e04fab72c125ff49f83adf6625ae62b417322c1724ded4c91eeb7d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = HttpRouteProps(
            http_api=http_api,
            route_key=route_key,
            authorization_scopes=authorization_scopes,
            authorizer=authorizer,
            integration=integration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *,
        http_methods: typing.Optional[typing.Sequence[HttpMethod]] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant access to invoke the route.

        This method requires that the authorizer of the route is undefined or is
        an ``HttpIamAuthorizer``.

        :param grantee: -
        :param http_methods: (experimental) The HTTP methods to allow. Default: - the HttpMethod of the route

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53257a740a0bf9e3076f5e9960cdc2b0c474378d558e854838154ba2bd8034cf)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        options = GrantInvokeOptions(http_methods=http_methods)

        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvoke", [grantee, options]))

    @builtins.property
    @jsii.member(jsii_name="httpApi")
    def http_api(self) -> IHttpApi:
        '''(experimental) The HTTP API associated with this route.

        :stability: experimental
        '''
        return typing.cast(IHttpApi, jsii.get(self, "httpApi"))

    @builtins.property
    @jsii.member(jsii_name="routeArn")
    def route_arn(self) -> builtins.str:
        '''(experimental) Returns the arn of the route.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "routeArn"))

    @builtins.property
    @jsii.member(jsii_name="routeId")
    def route_id(self) -> builtins.str:
        '''(experimental) Id of the Route.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "routeId"))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> typing.Optional[builtins.str]:
        '''(experimental) Returns the path component of this HTTP route, ``undefined`` if the path is the catch-all route.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "path"))


@jsii.implements(IHttpStage, IStage)
class HttpStage(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-alpha.HttpStage",
):
    '''(experimental) Represents a stage where an instance of the API is deployed.

    :stability: experimental
    :resource: AWS::ApiGatewayV2::Stage
    :exampleMetadata: infused

    Example::

        # api: apigwv2.HttpApi
        
        
        apigwv2.HttpStage(self, "Stage",
            http_api=api,
            stage_name="beta"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        http_api: IHttpApi,
        stage_name: typing.Optional[builtins.str] = None,
        auto_deploy: typing.Optional[builtins.bool] = None,
        domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param http_api: (experimental) The HTTP API to which this stage is associated.
        :param stage_name: (experimental) The name of the stage. See ``StageName`` class for more details. Default: '$default' the default stage of the API. This stage will have the URL at the root of the API endpoint.
        :param auto_deploy: (experimental) Whether updates to an API automatically trigger a new deployment. Default: false
        :param domain_mapping: (experimental) The options for custom domain and api mapping. Default: - no custom domain and api mapping configuration
        :param throttle: (experimental) Throttle settings for the routes of this stage. Default: - no throttling configuration

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed92fb335fa6855175afbb033d45447922cc6911de5d516e1c4dd76351a72aa1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = HttpStageProps(
            http_api=http_api,
            stage_name=stage_name,
            auto_deploy=auto_deploy,
            domain_mapping=domain_mapping,
            throttle=throttle,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromHttpStageAttributes")
    @builtins.classmethod
    def from_http_stage_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api: IHttpApi,
        stage_name: builtins.str,
    ) -> IHttpStage:
        '''(experimental) Import an existing stage into this CDK app.

        :param scope: -
        :param id: -
        :param api: (experimental) The API to which this stage is associated.
        :param stage_name: (experimental) The name of the stage.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__456b0db547449fda45bdfda459b2a51921656ff642e3c234362965315dbd5cd5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = HttpStageAttributes(api=api, stage_name=stage_name)

        return typing.cast(IHttpStage, jsii.sinvoke(cls, "fromHttpStageAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this HTTP Api Gateway Stage.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13222b5ec0bde39f747497ef32fa2559d2b7146ce09903ba475536fb3869b080)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricClientError")
    def metric_client_error(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the number of client-side errors captured in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricClientError", [props]))

    @jsii.member(jsii_name="metricCount")
    def metric_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the total number API requests in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricCount", [props]))

    @jsii.member(jsii_name="metricDataProcessed")
    def metric_data_processed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the amount of data processed in bytes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricDataProcessed", [props]))

    @jsii.member(jsii_name="metricIntegrationLatency")
    def metric_integration_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the time between when API Gateway relays a request to the backend and when it receives a response from the backend.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricIntegrationLatency", [props]))

    @jsii.member(jsii_name="metricLatency")
    def metric_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) The time between when API Gateway receives a request from a client and when it returns a response to the client.

        The latency includes the integration latency and other API Gateway overhead.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricLatency", [props]))

    @jsii.member(jsii_name="metricServerError")
    def metric_server_error(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Metric for the number of server-side errors captured in a given period.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Use the factory functions on the ``Stats`` object to construct valid input strings. Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricServerError", [props]))

    @builtins.property
    @jsii.member(jsii_name="api")
    def api(self) -> IHttpApi:
        '''(experimental) The API this stage is associated to.

        :stability: experimental
        '''
        return typing.cast(IHttpApi, jsii.get(self, "api"))

    @builtins.property
    @jsii.member(jsii_name="baseApi")
    def _base_api(self) -> IApi:
        '''
        :stability: experimental
        '''
        return typing.cast(IApi, jsii.get(self, "baseApi"))

    @builtins.property
    @jsii.member(jsii_name="domainUrl")
    def domain_url(self) -> builtins.str:
        '''(experimental) The custom domain URL to this stage.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainUrl"))

    @builtins.property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        '''(experimental) The name of the stage;

        its primary identifier.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "stageName"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''(experimental) The URL to this stage.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "url"))


__all__ = [
    "AddRoutesOptions",
    "ApiMapping",
    "ApiMappingAttributes",
    "ApiMappingProps",
    "AuthorizerPayloadVersion",
    "BatchHttpRouteOptions",
    "CorsHttpMethod",
    "CorsPreflightOptions",
    "DomainMappingOptions",
    "DomainName",
    "DomainNameAttributes",
    "DomainNameProps",
    "EndpointOptions",
    "EndpointType",
    "GrantInvokeOptions",
    "HttpApi",
    "HttpApiAttributes",
    "HttpApiProps",
    "HttpAuthorizer",
    "HttpAuthorizerAttributes",
    "HttpAuthorizerProps",
    "HttpAuthorizerType",
    "HttpConnectionType",
    "HttpIntegration",
    "HttpIntegrationProps",
    "HttpIntegrationSubtype",
    "HttpIntegrationType",
    "HttpMethod",
    "HttpNoneAuthorizer",
    "HttpRoute",
    "HttpRouteAuthorizerBindOptions",
    "HttpRouteAuthorizerConfig",
    "HttpRouteIntegration",
    "HttpRouteIntegrationBindOptions",
    "HttpRouteIntegrationConfig",
    "HttpRouteKey",
    "HttpRouteProps",
    "HttpStage",
    "HttpStageAttributes",
    "HttpStageOptions",
    "HttpStageProps",
    "IApi",
    "IApiMapping",
    "IAuthorizer",
    "IDomainName",
    "IHttpApi",
    "IHttpAuthorizer",
    "IHttpIntegration",
    "IHttpRoute",
    "IHttpRouteAuthorizer",
    "IHttpStage",
    "IIntegration",
    "IMappingValue",
    "IRoute",
    "IStage",
    "IVpcLink",
    "IWebSocketApi",
    "IWebSocketAuthorizer",
    "IWebSocketIntegration",
    "IWebSocketRoute",
    "IWebSocketRouteAuthorizer",
    "IWebSocketStage",
    "IntegrationCredentials",
    "MTLSConfig",
    "MappingValue",
    "ParameterMapping",
    "PayloadFormatVersion",
    "SecurityPolicy",
    "StageAttributes",
    "StageOptions",
    "ThrottleSettings",
    "VpcLink",
    "VpcLinkAttributes",
    "VpcLinkProps",
    "WebSocketApi",
    "WebSocketApiAttributes",
    "WebSocketApiKeySelectionExpression",
    "WebSocketApiProps",
    "WebSocketAuthorizer",
    "WebSocketAuthorizerAttributes",
    "WebSocketAuthorizerProps",
    "WebSocketAuthorizerType",
    "WebSocketIntegration",
    "WebSocketIntegrationProps",
    "WebSocketIntegrationType",
    "WebSocketNoneAuthorizer",
    "WebSocketRoute",
    "WebSocketRouteAuthorizerBindOptions",
    "WebSocketRouteAuthorizerConfig",
    "WebSocketRouteIntegration",
    "WebSocketRouteIntegrationBindOptions",
    "WebSocketRouteIntegrationConfig",
    "WebSocketRouteOptions",
    "WebSocketRouteProps",
    "WebSocketStage",
    "WebSocketStageAttributes",
    "WebSocketStageProps",
]

publication.publish()

def _typecheckingstub__742c0d28ff28876a0bc0d1152ef7b3343151f193a0e128ba64a6cbc4509c8f05(
    *,
    api_mapping_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75ffb83f83ec42f2a0382885c05d069ecb32c50d82d796df38b991d84782ded6(
    *,
    api: IApi,
    domain_name: IDomainName,
    api_mapping_key: typing.Optional[builtins.str] = None,
    stage: typing.Optional[IStage] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd6be8693e2cd2875856654344853bc620de9c6dd3e82fbd384cba9b5468a36d(
    *,
    integration: HttpRouteIntegration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8623074d52aadb0b4dc416f52273d5e1695739d7da72a818e4a16b0988313fa(
    *,
    allow_credentials: typing.Optional[builtins.bool] = None,
    allow_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    allow_methods: typing.Optional[typing.Sequence[CorsHttpMethod]] = None,
    allow_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
    expose_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    max_age: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9c022929eefc93f95859e1c88a0b0f15538c5b557fbe539653100b894c61520(
    *,
    domain_name: IDomainName,
    mapping_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3a28ea7d17c0cb32594b624176b2b5339560671719297d538c51a793079d6f8(
    *,
    name: builtins.str,
    regional_domain_name: builtins.str,
    regional_hosted_zone_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a18b13421aac912723b2ab35f8a14b008971c520719c36b6764e8ff2bd43194(
    *,
    certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
    certificate_name: typing.Optional[builtins.str] = None,
    endpoint_type: typing.Optional[EndpointType] = None,
    ownership_certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    security_policy: typing.Optional[SecurityPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a82686daa9fd8d0f3123464a3edac12340e9f588999872022e157589c9935c8a(
    *,
    http_methods: typing.Optional[typing.Sequence[HttpMethod]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca86693c779a127085f398e4f4b28effbcaffb7b0e4c3586085ba8720c18c3b6(
    *,
    http_api_id: builtins.str,
    api_endpoint: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61f68792e068176f35bfd5b9b8d36c51601ad6882e6aa3ce1c951683b5d199d2(
    *,
    api_name: typing.Optional[builtins.str] = None,
    cors_preflight: typing.Optional[typing.Union[CorsPreflightOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    create_default_stage: typing.Optional[builtins.bool] = None,
    default_authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    default_authorizer: typing.Optional[IHttpRouteAuthorizer] = None,
    default_domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    default_integration: typing.Optional[HttpRouteIntegration] = None,
    description: typing.Optional[builtins.str] = None,
    disable_execute_api_endpoint: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e213cc5ff1a6a50f727adfa1a93746afabbb568dc170da0d58f5c5f6b4a65877(
    *,
    authorizer_id: builtins.str,
    authorizer_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__270c2096601be45fba89ecb508234f5870eaabd6d21813bc090ce9b1a459264d(
    *,
    http_api: IHttpApi,
    identity_source: typing.Sequence[builtins.str],
    type: HttpAuthorizerType,
    authorizer_name: typing.Optional[builtins.str] = None,
    authorizer_uri: typing.Optional[builtins.str] = None,
    enable_simple_responses: typing.Optional[builtins.bool] = None,
    jwt_audience: typing.Optional[typing.Sequence[builtins.str]] = None,
    jwt_issuer: typing.Optional[builtins.str] = None,
    payload_format_version: typing.Optional[AuthorizerPayloadVersion] = None,
    results_cache_ttl: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e70b5fc9ef16c84251eedf90fb9f4578a5231e285c86d485055a9875610b863(
    *,
    http_api: IHttpApi,
    integration_type: HttpIntegrationType,
    connection_id: typing.Optional[builtins.str] = None,
    connection_type: typing.Optional[HttpConnectionType] = None,
    credentials: typing.Optional[IntegrationCredentials] = None,
    integration_subtype: typing.Optional[HttpIntegrationSubtype] = None,
    integration_uri: typing.Optional[builtins.str] = None,
    method: typing.Optional[HttpMethod] = None,
    parameter_mapping: typing.Optional[ParameterMapping] = None,
    payload_format_version: typing.Optional[PayloadFormatVersion] = None,
    secure_server_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__327eab42c70e54708c05239cc92e1d413d8f439a24b6448c6de2d0f2d4df7521(
    *,
    route: IHttpRoute,
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23fa1130cc8cec3f96c4c7be76f4fde0189dfa2fd6410ede8be1c8e24a88a0f2(
    *,
    authorization_type: builtins.str,
    authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    authorizer_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d2d16b160325ee41bba7780d2678d810d12da5f663f886f5c8a810a06c66fef(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fee001518b0d0335530b5174be6d0d04745ad94a5bffe05a6d9007712a52eb52(
    *,
    route: IHttpRoute,
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d07656a3841a48dd4643d0e10742dee8735d4fa1b6dec4e77afe67a3c12f2dd(
    *,
    payload_format_version: PayloadFormatVersion,
    type: HttpIntegrationType,
    connection_id: typing.Optional[builtins.str] = None,
    connection_type: typing.Optional[HttpConnectionType] = None,
    credentials: typing.Optional[IntegrationCredentials] = None,
    method: typing.Optional[HttpMethod] = None,
    parameter_mapping: typing.Optional[ParameterMapping] = None,
    secure_server_name: typing.Optional[builtins.str] = None,
    subtype: typing.Optional[HttpIntegrationSubtype] = None,
    uri: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__757949aa83516e4dc3de82eaf70c9ec58058087715b274d9a080b33530b01213(
    path: builtins.str,
    method: typing.Optional[HttpMethod] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a43a4a903025b4c98824c40d09ba7a3ec865a0a5902fb4f311846b446c460133(
    *,
    integration: HttpRouteIntegration,
    http_api: IHttpApi,
    route_key: HttpRouteKey,
    authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    authorizer: typing.Optional[IHttpRouteAuthorizer] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c475fcfbd8ec2d43f9f067afa8d49c21d334d5c85f25834be833f0c107d99e8e(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6eea31b2ea3d8439d0d065d266b0097b8fd2775bebde3b5b7cfc484683aa34a(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__102c1a776427fd4c0938e5abf575144e45fdb236c63258f1da261499f33717f0(
    role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38e19f865daecac4e9c0b7840b549ee7e3e17328107146b6aeed11be416a4830(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    key: builtins.str,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__214070b3203c10af4bde0b28ed256ac9a4d24597f026dd0b0cc830dd88c3212d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4af933305aeacd390d336f32a5829afa054de657121385d6ec7753a9ea26d601(
    variable_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ea57d3eb4bcfb04e995828dff02ab6f0787305f407450d33b5272726fe121ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd491365abe2954925b1f433ba7521a56e4bbc0bcdfddd61b667ca4f13903681(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e720451078130f0098a0b48416451612a00e6befa0c802ff75a2b864085649a5(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69c384039069eb05e230de4bc9ac53925e0d361bd038ed0a3b02e073b1525c71(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b36b16773b8a1c554f9a57b9e3d7a3722f155a3d65b1a10b4204ac3f1740616a(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3602fe53f550a6f339115089310b50937eb494d182495b9b3787a639c5dcaed(
    variable_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8181ef9cc8308f9477f0a1caad591787ed40d80e9353a4ab806411f93450058(
    obj: typing.Mapping[builtins.str, MappingValue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56ae57cc9968fa2fd30ad1d66784260b0e784ac1e0ae80923fa737f9a8ada22a(
    name: builtins.str,
    value: MappingValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f855f9472042f201eb931ccc90ac6f72c3684fdf5485ee6979662f843ed27cc(
    name: builtins.str,
    value: MappingValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea27856048c8e84cddc832b14d9115403f2b80ce39008d1d2a456c126be689c6(
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bbf5124407bf24ea9fa7d17aa1565a5ed9210655f4f602da854ad14a24db0d5(
    name: builtins.str,
    value: MappingValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3969677f031f21644ed17215886d65e2445e67dcf22241b2a6150248c6192f36(
    value: MappingValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e75c515536f95796a2a8f985b00f7829f0664a04b9a30bed03ea9ad1ce892d91(
    name: builtins.str,
    value: MappingValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48411845428e2e72182038805ca1f55aa523a254158b3148ec49d4ee874decc5(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46e584a752980831919a8156516ab93f44fb1a783b5798270ff450fdc6bc50d2(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__650e7e8cf5095b5caf036d1cdfea61cdc50d05db4e0b82311e5988ab562c7508(
    version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7bc86d60b044b6ce8b75e1e701218c18bc2ca9ef7cc2a9667e4858066891f46(
    *,
    stage_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a32c0806cbd09e57e1b6cb67e4b59ac7fdd424ef31f824f2caeda822945dbf65(
    *,
    auto_deploy: typing.Optional[builtins.bool] = None,
    domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ad556ef4d84d522901264cb64a96b656171558870186a72f596567dc19746a2(
    *,
    burst_limit: typing.Optional[jsii.Number] = None,
    rate_limit: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7e5cf8ebb393b1b711349f32ce6a5d91c23aa92cb3f1a5fb324d1ace8fa39e5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_link_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1b73cd3902808dcd9cedbbb002791b3c0b71ecf07dc9ee537153e45a37de0b7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    vpc_link_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb1536c4a56444b87ed12cf12ec84dcad1aeea01af7e687ab6bc5440355e7e11(
    *groups: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b26d604e4ca1a2688579e0987cdb68ab389de0e4b8cb68e274ece105bdd03cf(
    *subnets: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b806190a5cb732ad4de67d21bd895caa64bb12248a0d0ab31634597e02c8057e(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    vpc_link_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9aed9118f19188de6967aa0373708cfcd4ffb3d828b567d6cbc01404c7aa6581(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_link_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1178cce7f52c6ba72b835087f977643630d7f0c2665b967ecfee0bfe59093cb6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api_key_selection_expression: typing.Optional[WebSocketApiKeySelectionExpression] = None,
    api_name: typing.Optional[builtins.str] = None,
    connect_route_options: typing.Optional[typing.Union[WebSocketRouteOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    default_route_options: typing.Optional[typing.Union[WebSocketRouteOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    disconnect_route_options: typing.Optional[typing.Union[WebSocketRouteOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    route_selection_expression: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53d1a9fe1fdf41c0b5a739761d4875fb19c206a09c26c51425f989503e6b976b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    web_socket_id: builtins.str,
    api_endpoint: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3fea69a2469b346680a0c3465ad0d8edf75af46ec799894b3faabfa5c26ec77(
    route_key: builtins.str,
    *,
    integration: WebSocketRouteIntegration,
    authorizer: typing.Optional[IWebSocketRouteAuthorizer] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3519e657dc5ef6b61e34eb3fc9f6d114f2ebbf762f5ca278412f276b78b73bd7(
    identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25c26b71a707cd073d476cfe86d40884d0adc369830b3b667bfcc8d3d5069fe3(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae0c8df0ca0e715101942e90c3ba6802a24a7d17b7ccaf420c2de7498d0f3110(
    *,
    web_socket_id: builtins.str,
    api_endpoint: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34791e0880629c49a9f044c4e76a43e531d8704f81a7f9c57e446e0f8af0541c(
    custom_api_key_selector: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92cd23b712e91b17d8d403f5d44376505198f2e4d79f2370e3ce6a05ea6ddc2a(
    *,
    api_key_selection_expression: typing.Optional[WebSocketApiKeySelectionExpression] = None,
    api_name: typing.Optional[builtins.str] = None,
    connect_route_options: typing.Optional[typing.Union[WebSocketRouteOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    default_route_options: typing.Optional[typing.Union[WebSocketRouteOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    disconnect_route_options: typing.Optional[typing.Union[WebSocketRouteOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    route_selection_expression: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f24f7e7421170c9759c052f1d385a1f7e94dbd5eb18e0b47be9cab3ee8826990(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    identity_source: typing.Sequence[builtins.str],
    type: WebSocketAuthorizerType,
    web_socket_api: IWebSocketApi,
    authorizer_name: typing.Optional[builtins.str] = None,
    authorizer_uri: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e383ace2ee0471b5314c8dcb5e8b4c903443f7f45d06e85ce1160c2494ade7c3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    authorizer_id: builtins.str,
    authorizer_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec6cd687f35d4560bc6ed8b97968247261b8e88313cf6380b0c261222b1d373c(
    *,
    authorizer_id: builtins.str,
    authorizer_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e02c909494ad68823621decb1cf4f3c9d5a9383ba2429deace659f406a376cde(
    *,
    identity_source: typing.Sequence[builtins.str],
    type: WebSocketAuthorizerType,
    web_socket_api: IWebSocketApi,
    authorizer_name: typing.Optional[builtins.str] = None,
    authorizer_uri: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__870fc94d82010681246ecba710a6ed2fbd784a22488897490747220c5a9bb1a9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    integration_type: WebSocketIntegrationType,
    integration_uri: builtins.str,
    web_socket_api: IWebSocketApi,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__809d7a61872d8b86104362e83bf279e0275cab4ee56d78bb981f42a476435905(
    *,
    integration_type: WebSocketIntegrationType,
    integration_uri: builtins.str,
    web_socket_api: IWebSocketApi,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89ed8dea5fd2abdd3d7348cec8375728ea8c56911ab73c2e7661f42936a36951(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    route_key: builtins.str,
    web_socket_api: IWebSocketApi,
    api_key_required: typing.Optional[builtins.bool] = None,
    integration: WebSocketRouteIntegration,
    authorizer: typing.Optional[IWebSocketRouteAuthorizer] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fccd4465748920ec078ce3c095e6d5997201164b60c9937b341677d4bed18d2d(
    *,
    route: IWebSocketRoute,
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31b7978ca3879b28e59655ad191a6a2a4b1f15e48c662e792f29609537418e7b(
    *,
    authorization_type: builtins.str,
    authorizer_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c197ca72497cd4c42d540f6e0560e6883980b3d825f1228e227525877aff3ac4(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9af6c9ac36dba4ed1e02e99de4fc973a26bd4423e8609681f9bddbf43144cd7(
    *,
    route: IWebSocketRoute,
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9151ff6a777a4992f010dc6dd1747375682b7a6c0d45bfbda07ab180448bf7f(
    *,
    type: WebSocketIntegrationType,
    uri: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__015136d7cb99d78ecaebab742d43a14edcb81e619d7967b3b64eaf687c0d9ee3(
    *,
    integration: WebSocketRouteIntegration,
    authorizer: typing.Optional[IWebSocketRouteAuthorizer] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16bac6f0c09166c97608a842bf64940ba77c4a2c9803f76985adfdc50657856b(
    *,
    integration: WebSocketRouteIntegration,
    authorizer: typing.Optional[IWebSocketRouteAuthorizer] = None,
    route_key: builtins.str,
    web_socket_api: IWebSocketApi,
    api_key_required: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48af0e7d3ce9ece527270c25928990cf8b605f1e3585927c1afcc3ffef087cf6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    stage_name: builtins.str,
    web_socket_api: IWebSocketApi,
    auto_deploy: typing.Optional[builtins.bool] = None,
    domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96d2e4a524a0487b6a3e41257302724f03ec2dea315215c2348c1e882d82a509(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api: IWebSocketApi,
    stage_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__385987aac133337ee8f5f880408bf66af8f3e3a5651bc827a3bc5af110334a17(
    identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b080276ad15c8223193f7ed4fefbc76be9f47841814221e9a4dee06286100c93(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e391865a4ae4984a049207c6b5c3768117999fb528b5847ca1a6c7c35d2f82b(
    *,
    stage_name: builtins.str,
    api: IWebSocketApi,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__782ab449d8fa4cf0a46fbab6526bdc241efef3893414586af02c8f715748ee2a(
    *,
    auto_deploy: typing.Optional[builtins.bool] = None,
    domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    stage_name: builtins.str,
    web_socket_api: IWebSocketApi,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca8141f667bdde01ab0100d57a58a21f4b9acc231a1bbfb55a1925c258a680c6(
    *,
    integration: HttpRouteIntegration,
    path: builtins.str,
    authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    authorizer: typing.Optional[IHttpRouteAuthorizer] = None,
    methods: typing.Optional[typing.Sequence[HttpMethod]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbff8656b4f6706b46963d8d04c49514410f8af75cfeb33a4c2fe1a07e9f33ac(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api: IApi,
    domain_name: IDomainName,
    api_mapping_key: typing.Optional[builtins.str] = None,
    stage: typing.Optional[IStage] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a142e4a61436ea624a748446cb739233abd5326d66a7e1a91f9c88642f61ca94(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api_mapping_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9d717e977e1b3688e10b96a28c290636a0c8ffb230b0e32f751c93cfed6ae39(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_name: builtins.str,
    mtls: typing.Optional[typing.Union[MTLSConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
    certificate_name: typing.Optional[builtins.str] = None,
    endpoint_type: typing.Optional[EndpointType] = None,
    ownership_certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    security_policy: typing.Optional[SecurityPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a75b51d5333f983b1ad28c7723855075bb1accd439fd505ecabd1a569a79bab5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    regional_domain_name: builtins.str,
    regional_hosted_zone_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__698fe2808c79855db0ec402620f39e09a615424a13b6af162379044207a388e5(
    *,
    certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
    certificate_name: typing.Optional[builtins.str] = None,
    endpoint_type: typing.Optional[EndpointType] = None,
    ownership_certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    security_policy: typing.Optional[SecurityPolicy] = None,
    domain_name: builtins.str,
    mtls: typing.Optional[typing.Union[MTLSConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5003409414773984b85252451580f75369de42c80978f161fece7261c553c54(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api_name: typing.Optional[builtins.str] = None,
    cors_preflight: typing.Optional[typing.Union[CorsPreflightOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    create_default_stage: typing.Optional[builtins.bool] = None,
    default_authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    default_authorizer: typing.Optional[IHttpRouteAuthorizer] = None,
    default_domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    default_integration: typing.Optional[HttpRouteIntegration] = None,
    description: typing.Optional[builtins.str] = None,
    disable_execute_api_endpoint: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecd315f15fe552c95da2ac31778a118bb3415d560941e8d18e9c71e631481225(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    http_api_id: builtins.str,
    api_endpoint: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bab5e6089f6e913d418934d66da25f8a39159ad3bd9f9f115cbcde831da78e0(
    id: builtins.str,
    *,
    stage_name: typing.Optional[builtins.str] = None,
    auto_deploy: typing.Optional[builtins.bool] = None,
    domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7709e3cbcd45c7d4a9b816ad94388873b7fd0558ca6fdcb427f2d5ca6e8df6a(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03f7fb4792b9161dda177d8df2f5bc58091a4f546c4ca11ee18afaa4e0bf5e28(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    http_api: IHttpApi,
    identity_source: typing.Sequence[builtins.str],
    type: HttpAuthorizerType,
    authorizer_name: typing.Optional[builtins.str] = None,
    authorizer_uri: typing.Optional[builtins.str] = None,
    enable_simple_responses: typing.Optional[builtins.bool] = None,
    jwt_audience: typing.Optional[typing.Sequence[builtins.str]] = None,
    jwt_issuer: typing.Optional[builtins.str] = None,
    payload_format_version: typing.Optional[AuthorizerPayloadVersion] = None,
    results_cache_ttl: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efb4a2f65822f686a6ffa7ada308b84e89325054661df552cb9bc6286414ff5b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    authorizer_id: builtins.str,
    authorizer_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68b934e47d5c501cf4c24923fe5b089fdb197a5624c649d8f83e58305cd890d5(
    *,
    stage_name: builtins.str,
    api: IHttpApi,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e64c35e906d5449f8f7b3901603109565a527cbb27318f310243b054419c4a7(
    *,
    auto_deploy: typing.Optional[builtins.bool] = None,
    domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    stage_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__925560a3ec43c8b350658e7729b7c093c0eb2dc51b442b9b5877c46ec328fbb4(
    *,
    auto_deploy: typing.Optional[builtins.bool] = None,
    domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    stage_name: typing.Optional[builtins.str] = None,
    http_api: IHttpApi,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e68d78a6fdd2cf02aa0a9db3e16ddc620002125429503856eb2206ca6638a462(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *,
    http_methods: typing.Optional[typing.Sequence[HttpMethod]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3de74d25b3d7d1e17696a2da7bd0666d13d0467eed87993389dc688e2ffcf281(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    http_api: IHttpApi,
    integration_type: HttpIntegrationType,
    connection_id: typing.Optional[builtins.str] = None,
    connection_type: typing.Optional[HttpConnectionType] = None,
    credentials: typing.Optional[IntegrationCredentials] = None,
    integration_subtype: typing.Optional[HttpIntegrationSubtype] = None,
    integration_uri: typing.Optional[builtins.str] = None,
    method: typing.Optional[HttpMethod] = None,
    parameter_mapping: typing.Optional[ParameterMapping] = None,
    payload_format_version: typing.Optional[PayloadFormatVersion] = None,
    secure_server_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d456143a18e04fab72c125ff49f83adf6625ae62b417322c1724ded4c91eeb7d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    http_api: IHttpApi,
    route_key: HttpRouteKey,
    authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    authorizer: typing.Optional[IHttpRouteAuthorizer] = None,
    integration: HttpRouteIntegration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53257a740a0bf9e3076f5e9960cdc2b0c474378d558e854838154ba2bd8034cf(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *,
    http_methods: typing.Optional[typing.Sequence[HttpMethod]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed92fb335fa6855175afbb033d45447922cc6911de5d516e1c4dd76351a72aa1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    http_api: IHttpApi,
    stage_name: typing.Optional[builtins.str] = None,
    auto_deploy: typing.Optional[builtins.bool] = None,
    domain_mapping: typing.Optional[typing.Union[DomainMappingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    throttle: typing.Optional[typing.Union[ThrottleSettings, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__456b0db547449fda45bdfda459b2a51921656ff642e3c234362965315dbd5cd5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api: IHttpApi,
    stage_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13222b5ec0bde39f747497ef32fa2559d2b7146ce09903ba475536fb3869b080(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass
