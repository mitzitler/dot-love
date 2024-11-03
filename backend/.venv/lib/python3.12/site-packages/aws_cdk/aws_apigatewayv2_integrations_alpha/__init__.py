'''
# AWS APIGatewayv2 Integrations

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

## Table of Contents

* [HTTP APIs](#http-apis)

  * [Lambda Integration](#lambda)
  * [HTTP Proxy Integration](#http-proxy)
  * [Private Integration](#private-integration)
  * [Request Parameters](#request-parameters)
* [WebSocket APIs](#websocket-apis)

  * [Lambda WebSocket Integration](#lambda-websocket-integration)

## HTTP APIs

Integrations connect a route to backend resources. HTTP APIs support Lambda proxy, AWS service, and HTTP proxy integrations. HTTP proxy integrations are also known as private integrations.

### Lambda

Lambda integrations enable integrating an HTTP API route with a Lambda function. When a client invokes the route, the
API Gateway service forwards the request to the Lambda function and returns the function's response to the client.

The API Gateway service will invoke the lambda function with an event payload of a specific format. The service expects
the function to respond in a specific format. The details on this format is available at [Working with AWS Lambda
proxy integrations](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html).

The following code configures a route `GET /books` with a Lambda proxy integration.

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration

# books_default_fn: lambda.Function

books_integration = HttpLambdaIntegration("BooksIntegration", books_default_fn)

http_api = apigwv2.HttpApi(self, "HttpApi")

http_api.add_routes(
    path="/books",
    methods=[apigwv2.HttpMethod.GET],
    integration=books_integration
)
```

### HTTP Proxy

HTTP Proxy integrations enables connecting an HTTP API route to a publicly routable HTTP endpoint. When a client
invokes the route, the API Gateway service forwards the entire request and response between the API Gateway endpoint
and the integrating HTTP endpoint. More information can be found at [Working with HTTP proxy
integrations](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-http.html).

The following code configures a route `GET /books` with an HTTP proxy integration to an HTTP endpoint
`get-books-proxy.example.com`.

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration


books_integration = HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.example.com")

http_api = apigwv2.HttpApi(self, "HttpApi")

http_api.add_routes(
    path="/books",
    methods=[apigwv2.HttpMethod.GET],
    integration=books_integration
)
```

### Private Integration

Private integrations enable integrating an HTTP API route with private resources in a VPC, such as Application Load Balancers or
Amazon ECS container-based applications.  Using private integrations, resources in a VPC can be exposed for access by
clients outside of the VPC.

The following integrations are supported for private resources in a VPC.

#### Application Load Balancer

The following code is a basic application load balancer private integration of HTTP API:

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpAlbIntegration


vpc = ec2.Vpc(self, "VPC")
lb = elbv2.ApplicationLoadBalancer(self, "lb", vpc=vpc)
listener = lb.add_listener("listener", port=80)
listener.add_targets("target",
    port=80
)

http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
    default_integration=HttpAlbIntegration("DefaultIntegration", listener)
)
```

When an imported load balancer is used, the `vpc` option must be specified for `HttpAlbIntegration`.

#### Network Load Balancer

The following code is a basic network load balancer private integration of HTTP API:

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpNlbIntegration


vpc = ec2.Vpc(self, "VPC")
lb = elbv2.NetworkLoadBalancer(self, "lb", vpc=vpc)
listener = lb.add_listener("listener", port=80)
listener.add_targets("target",
    port=80
)

http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
    default_integration=HttpNlbIntegration("DefaultIntegration", listener)
)
```

When an imported load balancer is used, the `vpc` option must be specified for `HttpNlbIntegration`.

#### Cloud Map Service Discovery

The following code is a basic discovery service private integration of HTTP API:

```python
import aws_cdk.aws_servicediscovery as servicediscovery
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpServiceDiscoveryIntegration


vpc = ec2.Vpc(self, "VPC")
vpc_link = apigwv2.VpcLink(self, "VpcLink", vpc=vpc)
namespace = servicediscovery.PrivateDnsNamespace(self, "Namespace",
    name="boobar.com",
    vpc=vpc
)
service = namespace.create_service("Service")

http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
    default_integration=HttpServiceDiscoveryIntegration("DefaultIntegration", service,
        vpc_link=vpc_link
    )
)
```

### Request Parameters

Request parameter mapping allows API requests from clients to be modified before they reach backend integrations.
Parameter mapping can be used to specify modifications to request parameters. See [Transforming API requests and
responses](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html).

The following example creates a new header - `header2` - as a copy of `header1` and removes `header1`.

```python
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
```

To add mapping keys and values not yet supported by the CDK, use the `custom()` method:

```python
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
```

## WebSocket APIs

WebSocket integrations connect a route to backend resources. The following integrations are supported in the CDK.

### Lambda WebSocket Integration

Lambda integrations enable integrating a WebSocket API route with a Lambda function. When a client connects/disconnects
or sends message specific to a route, the API Gateway service forwards the request to the Lambda function

The API Gateway service will invoke the lambda function with an event payload of a specific format.

The following code configures a `sendmessage` route with a Lambda integration

```python
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

import aws_cdk.aws_apigatewayv2_alpha as _aws_cdk_aws_apigatewayv2_alpha_050969fe
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_servicediscovery as _aws_cdk_aws_servicediscovery_ceddda9d
import constructs as _constructs_77d1e7e8


class HttpAlbIntegration(
    _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegration,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpAlbIntegration",
):
    '''(experimental) The Application Load Balancer integration resource for HTTP API.

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

    def __init__(
        self,
        id: builtins.str,
        listener: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener,
        *,
        method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
        parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
    ) -> None:
        '''
        :param id: id of the underlying integration construct.
        :param listener: the ELB application listener.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1051b1480a8cd47d711a84960fb401dc211dc0ba51fe7f789e2f339e045f4cca)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument listener", value=listener, expected_type=type_hints["listener"])
        props = HttpAlbIntegrationProps(
            method=method,
            parameter_mapping=parameter_mapping,
            secure_server_name=secure_server_name,
            vpc_link=vpc_link,
        )

        jsii.create(self.__class__, self, [id, listener, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _aws_cdk_aws_apigatewayv2_alpha_050969fe.IHttpRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationConfig:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationConfig, jsii.invoke(self, "bind", [options]))

    @builtins.property
    @jsii.member(jsii_name="connectionType")
    def _connection_type(
        self,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpConnectionType:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpConnectionType, jsii.get(self, "connectionType"))

    @_connection_type.setter
    def _connection_type(
        self,
        value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpConnectionType,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36449d0ed58756fe2f7fd192ea96aa9ea11f4987ffa1ac2965d2ab21b8270669)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionType", value)

    @builtins.property
    @jsii.member(jsii_name="httpMethod")
    def _http_method(self) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod, jsii.get(self, "httpMethod"))

    @_http_method.setter
    def _http_method(
        self,
        value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5dc163e7b5e827e8fb331531e706af6b8aed694b5df252879219c3a88c32b21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMethod", value)

    @builtins.property
    @jsii.member(jsii_name="integrationType")
    def _integration_type(
        self,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpIntegrationType:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpIntegrationType, jsii.get(self, "integrationType"))

    @_integration_type.setter
    def _integration_type(
        self,
        value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpIntegrationType,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22c266ae5ba72177fabe295e753bef793d5918f88d21c8d327d83f240cec5836)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrationType", value)

    @builtins.property
    @jsii.member(jsii_name="payloadFormatVersion")
    def _payload_format_version(
        self,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion, jsii.get(self, "payloadFormatVersion"))

    @_payload_format_version.setter
    def _payload_format_version(
        self,
        value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__131dd3859117b1c3dc8515c646fed00f9a95fe26870e5502a1c3005fbe9b464c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "payloadFormatVersion", value)


class HttpLambdaIntegration(
    _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegration,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpLambdaIntegration",
):
    '''(experimental) The Lambda Proxy integration resource for HTTP API.

    :stability: experimental
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
        id: builtins.str,
        handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        *,
        parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
        payload_format_version: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion] = None,
    ) -> None:
        '''
        :param id: id of the underlying integration construct.
        :param handler: the Lambda handler to integrate with.
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param payload_format_version: (experimental) Version of the payload sent to the lambda handler. Default: PayloadFormatVersion.VERSION_2_0

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42f60194a638b05797e7ab331280416ee3fbd1b288d018b79a6abec4b2cd71b2)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
        props = HttpLambdaIntegrationProps(
            parameter_mapping=parameter_mapping,
            payload_format_version=payload_format_version,
        )

        jsii.create(self.__class__, self, [id, handler, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _aws_cdk_aws_apigatewayv2_alpha_050969fe.IHttpRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationConfig:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        _ = _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationConfig, jsii.invoke(self, "bind", [_]))

    @jsii.member(jsii_name="completeBind")
    def _complete_bind(
        self,
        *,
        route: _aws_cdk_aws_apigatewayv2_alpha_050969fe.IHttpRoute,
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
        options = _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(None, jsii.invoke(self, "completeBind", [options]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpLambdaIntegrationProps",
    jsii_struct_bases=[],
    name_mapping={
        "parameter_mapping": "parameterMapping",
        "payload_format_version": "payloadFormatVersion",
    },
)
class HttpLambdaIntegrationProps:
    def __init__(
        self,
        *,
        parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
        payload_format_version: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion] = None,
    ) -> None:
        '''(experimental) Lambda Proxy integration properties.

        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param payload_format_version: (experimental) Version of the payload sent to the lambda handler. Default: PayloadFormatVersion.VERSION_2_0

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            import aws_cdk.aws_apigatewayv2_integrations_alpha as apigatewayv2_integrations_alpha
            
            # parameter_mapping: apigatewayv2_alpha.ParameterMapping
            # payload_format_version: apigatewayv2_alpha.PayloadFormatVersion
            
            http_lambda_integration_props = apigatewayv2_integrations_alpha.HttpLambdaIntegrationProps(
                parameter_mapping=parameter_mapping,
                payload_format_version=payload_format_version
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a21cbac976f3b5b37bd0bba7a22ddc71aec8b09a5fa6bb1dacddf8c32e9f716)
            check_type(argname="argument parameter_mapping", value=parameter_mapping, expected_type=type_hints["parameter_mapping"])
            check_type(argname="argument payload_format_version", value=payload_format_version, expected_type=type_hints["payload_format_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if payload_format_version is not None:
            self._values["payload_format_version"] = payload_format_version

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping], result)

    @builtins.property
    def payload_format_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion]:
        '''(experimental) Version of the payload sent to the lambda handler.

        :default: PayloadFormatVersion.VERSION_2_0

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
        :stability: experimental
        '''
        result = self._values.get("payload_format_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpLambdaIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HttpNlbIntegration(
    _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegration,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpNlbIntegration",
):
    '''(experimental) The Network Load Balancer integration resource for HTTP API.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpNlbIntegration
        
        
        vpc = ec2.Vpc(self, "VPC")
        lb = elbv2.NetworkLoadBalancer(self, "lb", vpc=vpc)
        listener = lb.add_listener("listener", port=80)
        listener.add_targets("target",
            port=80
        )
        
        http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
            default_integration=HttpNlbIntegration("DefaultIntegration", listener)
        )
    '''

    def __init__(
        self,
        id: builtins.str,
        listener: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.INetworkListener,
        *,
        method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
        parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
    ) -> None:
        '''
        :param id: id of the underlying integration construct.
        :param listener: the ELB network listener.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23538678538c3eeb8f55f23ba4c32b6153d35b1cb8bde3177648a1aa3f2dbf74)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument listener", value=listener, expected_type=type_hints["listener"])
        props = HttpNlbIntegrationProps(
            method=method,
            parameter_mapping=parameter_mapping,
            secure_server_name=secure_server_name,
            vpc_link=vpc_link,
        )

        jsii.create(self.__class__, self, [id, listener, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _aws_cdk_aws_apigatewayv2_alpha_050969fe.IHttpRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationConfig:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationConfig, jsii.invoke(self, "bind", [options]))

    @builtins.property
    @jsii.member(jsii_name="connectionType")
    def _connection_type(
        self,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpConnectionType:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpConnectionType, jsii.get(self, "connectionType"))

    @_connection_type.setter
    def _connection_type(
        self,
        value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpConnectionType,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e17455381dfbb8221af8a8b2fedb753c2c15627351dd4ea328f512f08c1b8aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionType", value)

    @builtins.property
    @jsii.member(jsii_name="httpMethod")
    def _http_method(self) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod, jsii.get(self, "httpMethod"))

    @_http_method.setter
    def _http_method(
        self,
        value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e839b5ca71d9a12744874723d727aff24d662d22cb48e89b5c2079498a9ea169)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMethod", value)

    @builtins.property
    @jsii.member(jsii_name="integrationType")
    def _integration_type(
        self,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpIntegrationType:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpIntegrationType, jsii.get(self, "integrationType"))

    @_integration_type.setter
    def _integration_type(
        self,
        value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpIntegrationType,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dd29f9644934e9af4e806c5447a3f1b4a02bff13d0a48ec96e6841ab3feda06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrationType", value)

    @builtins.property
    @jsii.member(jsii_name="payloadFormatVersion")
    def _payload_format_version(
        self,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion, jsii.get(self, "payloadFormatVersion"))

    @_payload_format_version.setter
    def _payload_format_version(
        self,
        value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9714bb1299b13b98b6badb1aeea61d4d940debe0b5ae0cfb9378612ba232941)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "payloadFormatVersion", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpPrivateIntegrationOptions",
    jsii_struct_bases=[],
    name_mapping={
        "method": "method",
        "parameter_mapping": "parameterMapping",
        "secure_server_name": "secureServerName",
        "vpc_link": "vpcLink",
    },
)
class HttpPrivateIntegrationOptions:
    def __init__(
        self,
        *,
        method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
        parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
    ) -> None:
        '''(experimental) Base options for private integration.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            import aws_cdk.aws_apigatewayv2_integrations_alpha as apigatewayv2_integrations_alpha
            
            # parameter_mapping: apigatewayv2_alpha.ParameterMapping
            # vpc_link: apigatewayv2_alpha.VpcLink
            
            http_private_integration_options = apigatewayv2_integrations_alpha.HttpPrivateIntegrationOptions(
                method=apigatewayv2_alpha.HttpMethod.ANY,
                parameter_mapping=parameter_mapping,
                secure_server_name="secureServerName",
                vpc_link=vpc_link
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af9150f33d84babdf3b7e860f41b0c38fa3a575b4c8540f59437e965167069aa)
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument parameter_mapping", value=parameter_mapping, expected_type=type_hints["parameter_mapping"])
            check_type(argname="argument secure_server_name", value=secure_server_name, expected_type=type_hints["secure_server_name"])
            check_type(argname="argument vpc_link", value=vpc_link, expected_type=type_hints["vpc_link"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if method is not None:
            self._values["method"] = method
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if vpc_link is not None:
            self._values["vpc_link"] = vpc_link

    @builtins.property
    def method(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod], result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping], result)

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
    def vpc_link(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink]:
        '''(experimental) The vpc link to be used for the private integration.

        :default: - a new VpcLink is created

        :stability: experimental
        '''
        result = self._values.get("vpc_link")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpPrivateIntegrationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HttpServiceDiscoveryIntegration(
    _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegration,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpServiceDiscoveryIntegration",
):
    '''(experimental) The Service Discovery integration resource for HTTP API.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_servicediscovery as servicediscovery
        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpServiceDiscoveryIntegration
        
        
        vpc = ec2.Vpc(self, "VPC")
        vpc_link = apigwv2.VpcLink(self, "VpcLink", vpc=vpc)
        namespace = servicediscovery.PrivateDnsNamespace(self, "Namespace",
            name="boobar.com",
            vpc=vpc
        )
        service = namespace.create_service("Service")
        
        http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
            default_integration=HttpServiceDiscoveryIntegration("DefaultIntegration", service,
                vpc_link=vpc_link
            )
        )
    '''

    def __init__(
        self,
        id: builtins.str,
        service: _aws_cdk_aws_servicediscovery_ceddda9d.IService,
        *,
        method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
        parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
    ) -> None:
        '''
        :param id: id of the underlying integration construct.
        :param service: the service discovery resource to integrate with.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00e34a738f2c9fe152b2ce2db7622b8c95db63b3e1b8768e2df2dd40d2776b14)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
        props = HttpServiceDiscoveryIntegrationProps(
            method=method,
            parameter_mapping=parameter_mapping,
            secure_server_name=secure_server_name,
            vpc_link=vpc_link,
        )

        jsii.create(self.__class__, self, [id, service, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _aws_cdk_aws_apigatewayv2_alpha_050969fe.IHttpRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationConfig:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        _ = _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationConfig, jsii.invoke(self, "bind", [_]))

    @builtins.property
    @jsii.member(jsii_name="connectionType")
    def _connection_type(
        self,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpConnectionType:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpConnectionType, jsii.get(self, "connectionType"))

    @_connection_type.setter
    def _connection_type(
        self,
        value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpConnectionType,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca1b680e984ff68c7d5229fa97abf6f06682d63c16b5f8eefd90b5b36a6f16e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionType", value)

    @builtins.property
    @jsii.member(jsii_name="httpMethod")
    def _http_method(self) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod, jsii.get(self, "httpMethod"))

    @_http_method.setter
    def _http_method(
        self,
        value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdfe129511d17d3c6412bff75ad53162fb83e1d1846ad686c5e007d33bd43690)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMethod", value)

    @builtins.property
    @jsii.member(jsii_name="integrationType")
    def _integration_type(
        self,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpIntegrationType:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpIntegrationType, jsii.get(self, "integrationType"))

    @_integration_type.setter
    def _integration_type(
        self,
        value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpIntegrationType,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__098da7a8326a68b12492150350f132c4b8357f8c0cfdd6a1c04b9fbf3aed651b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrationType", value)

    @builtins.property
    @jsii.member(jsii_name="payloadFormatVersion")
    def _payload_format_version(
        self,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion, jsii.get(self, "payloadFormatVersion"))

    @_payload_format_version.setter
    def _payload_format_version(
        self,
        value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__244bf7e00418063ee77d6ad97a4eb33851fd3d897cf6f5529a636591c85034e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "payloadFormatVersion", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpServiceDiscoveryIntegrationProps",
    jsii_struct_bases=[HttpPrivateIntegrationOptions],
    name_mapping={
        "method": "method",
        "parameter_mapping": "parameterMapping",
        "secure_server_name": "secureServerName",
        "vpc_link": "vpcLink",
    },
)
class HttpServiceDiscoveryIntegrationProps(HttpPrivateIntegrationOptions):
    def __init__(
        self,
        *,
        method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
        parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
    ) -> None:
        '''(experimental) Properties to initialize ``HttpServiceDiscoveryIntegration``.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_servicediscovery as servicediscovery
            from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpServiceDiscoveryIntegration
            
            
            vpc = ec2.Vpc(self, "VPC")
            vpc_link = apigwv2.VpcLink(self, "VpcLink", vpc=vpc)
            namespace = servicediscovery.PrivateDnsNamespace(self, "Namespace",
                name="boobar.com",
                vpc=vpc
            )
            service = namespace.create_service("Service")
            
            http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
                default_integration=HttpServiceDiscoveryIntegration("DefaultIntegration", service,
                    vpc_link=vpc_link
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa07da47c0416387096e305b20d645f5184937633df8dd9d37d28f3a51f39610)
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument parameter_mapping", value=parameter_mapping, expected_type=type_hints["parameter_mapping"])
            check_type(argname="argument secure_server_name", value=secure_server_name, expected_type=type_hints["secure_server_name"])
            check_type(argname="argument vpc_link", value=vpc_link, expected_type=type_hints["vpc_link"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if method is not None:
            self._values["method"] = method
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if vpc_link is not None:
            self._values["vpc_link"] = vpc_link

    @builtins.property
    def method(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod], result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping], result)

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
    def vpc_link(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink]:
        '''(experimental) The vpc link to be used for the private integration.

        :default: - a new VpcLink is created

        :stability: experimental
        '''
        result = self._values.get("vpc_link")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpServiceDiscoveryIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HttpUrlIntegration(
    _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegration,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpUrlIntegration",
):
    '''(experimental) The HTTP Proxy integration resource for HTTP API.

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

    def __init__(
        self,
        id: builtins.str,
        url: builtins.str,
        *,
        method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
        parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
    ) -> None:
        '''
        :param id: id of the underlying integration construct.
        :param url: the URL to proxy to.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70de8f547e3566414a23dadeb1c53c9110bd6b7229aa282940328f686467e80e)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        props = HttpUrlIntegrationProps(
            method=method, parameter_mapping=parameter_mapping
        )

        jsii.create(self.__class__, self, [id, url, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _aws_cdk_aws_apigatewayv2_alpha_050969fe.IHttpRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationConfig:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        _ = _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpRouteIntegrationConfig, jsii.invoke(self, "bind", [_]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpUrlIntegrationProps",
    jsii_struct_bases=[],
    name_mapping={"method": "method", "parameter_mapping": "parameterMapping"},
)
class HttpUrlIntegrationProps:
    def __init__(
        self,
        *,
        method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
        parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
    ) -> None:
        '''(experimental) Properties to initialize a new ``HttpProxyIntegration``.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            import aws_cdk.aws_apigatewayv2_integrations_alpha as apigatewayv2_integrations_alpha
            
            # parameter_mapping: apigatewayv2_alpha.ParameterMapping
            
            http_url_integration_props = apigatewayv2_integrations_alpha.HttpUrlIntegrationProps(
                method=apigatewayv2_alpha.HttpMethod.ANY,
                parameter_mapping=parameter_mapping
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__549a6c3540e3cf3d33b81f1183c39d8bc52fb71ae0bc3a6ac222f76c5f66ea70)
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument parameter_mapping", value=parameter_mapping, expected_type=type_hints["parameter_mapping"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if method is not None:
            self._values["method"] = method
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping

    @builtins.property
    def method(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod], result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpUrlIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WebSocketLambdaIntegration(
    _aws_cdk_aws_apigatewayv2_alpha_050969fe.WebSocketRouteIntegration,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.WebSocketLambdaIntegration",
):
    '''(experimental) Lambda WebSocket Integration.

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

    def __init__(
        self,
        id: builtins.str,
        handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        '''
        :param id: id of the underlying integration construct.
        :param handler: the Lambda function handler.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__609e98b096947b613313989e0e2e6a2a72a4cc23b9ac8f7d5cd433c61249043a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
        jsii.create(self.__class__, self, [id, handler])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _aws_cdk_aws_apigatewayv2_alpha_050969fe.IWebSocketRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.WebSocketRouteIntegrationConfig:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``WebSocketRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = _aws_cdk_aws_apigatewayv2_alpha_050969fe.WebSocketRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.WebSocketRouteIntegrationConfig, jsii.invoke(self, "bind", [options]))


class WebSocketMockIntegration(
    _aws_cdk_aws_apigatewayv2_alpha_050969fe.WebSocketRouteIntegration,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.WebSocketMockIntegration",
):
    '''(experimental) Mock WebSocket Integration.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_apigatewayv2_integrations_alpha as apigatewayv2_integrations_alpha
        
        web_socket_mock_integration = apigatewayv2_integrations_alpha.WebSocketMockIntegration("id")
    '''

    def __init__(self, id: builtins.str) -> None:
        '''
        :param id: id of the underlying integration construct.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69639dd59c40fb4ae670d012d6427385420cd2fb0351cc263cd8d27f49ed98b3)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [id])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: _aws_cdk_aws_apigatewayv2_alpha_050969fe.IWebSocketRoute,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_apigatewayv2_alpha_050969fe.WebSocketRouteIntegrationConfig:
        '''(experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``WebSocketRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = _aws_cdk_aws_apigatewayv2_alpha_050969fe.WebSocketRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(_aws_cdk_aws_apigatewayv2_alpha_050969fe.WebSocketRouteIntegrationConfig, jsii.invoke(self, "bind", [options]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpAlbIntegrationProps",
    jsii_struct_bases=[HttpPrivateIntegrationOptions],
    name_mapping={
        "method": "method",
        "parameter_mapping": "parameterMapping",
        "secure_server_name": "secureServerName",
        "vpc_link": "vpcLink",
    },
)
class HttpAlbIntegrationProps(HttpPrivateIntegrationOptions):
    def __init__(
        self,
        *,
        method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
        parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
    ) -> None:
        '''(experimental) Properties to initialize ``HttpAlbIntegration``.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

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
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee28cd43a256cf431e5012c28d37bdc89047f666d47217f86414c2a14605daf5)
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument parameter_mapping", value=parameter_mapping, expected_type=type_hints["parameter_mapping"])
            check_type(argname="argument secure_server_name", value=secure_server_name, expected_type=type_hints["secure_server_name"])
            check_type(argname="argument vpc_link", value=vpc_link, expected_type=type_hints["vpc_link"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if method is not None:
            self._values["method"] = method
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if vpc_link is not None:
            self._values["vpc_link"] = vpc_link

    @builtins.property
    def method(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod], result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping], result)

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
    def vpc_link(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink]:
        '''(experimental) The vpc link to be used for the private integration.

        :default: - a new VpcLink is created

        :stability: experimental
        '''
        result = self._values.get("vpc_link")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpAlbIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpNlbIntegrationProps",
    jsii_struct_bases=[HttpPrivateIntegrationOptions],
    name_mapping={
        "method": "method",
        "parameter_mapping": "parameterMapping",
        "secure_server_name": "secureServerName",
        "vpc_link": "vpcLink",
    },
)
class HttpNlbIntegrationProps(HttpPrivateIntegrationOptions):
    def __init__(
        self,
        *,
        method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
        parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
    ) -> None:
        '''(experimental) Properties to initialize ``HttpNlbIntegration``.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            import aws_cdk.aws_apigatewayv2_integrations_alpha as apigatewayv2_integrations_alpha
            
            # parameter_mapping: apigatewayv2_alpha.ParameterMapping
            # vpc_link: apigatewayv2_alpha.VpcLink
            
            http_nlb_integration_props = apigatewayv2_integrations_alpha.HttpNlbIntegrationProps(
                method=apigatewayv2_alpha.HttpMethod.ANY,
                parameter_mapping=parameter_mapping,
                secure_server_name="secureServerName",
                vpc_link=vpc_link
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18b50d7d30e6113bb374cb33044257c835e607dfbcfaf696fa3f6527d484232e)
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument parameter_mapping", value=parameter_mapping, expected_type=type_hints["parameter_mapping"])
            check_type(argname="argument secure_server_name", value=secure_server_name, expected_type=type_hints["secure_server_name"])
            check_type(argname="argument vpc_link", value=vpc_link, expected_type=type_hints["vpc_link"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if method is not None:
            self._values["method"] = method
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if vpc_link is not None:
            self._values["vpc_link"] = vpc_link

    @builtins.property
    def method(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod], result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping], result)

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
    def vpc_link(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink]:
        '''(experimental) The vpc link to be used for the private integration.

        :default: - a new VpcLink is created

        :stability: experimental
        '''
        result = self._values.get("vpc_link")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpNlbIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "HttpAlbIntegration",
    "HttpAlbIntegrationProps",
    "HttpLambdaIntegration",
    "HttpLambdaIntegrationProps",
    "HttpNlbIntegration",
    "HttpNlbIntegrationProps",
    "HttpPrivateIntegrationOptions",
    "HttpServiceDiscoveryIntegration",
    "HttpServiceDiscoveryIntegrationProps",
    "HttpUrlIntegration",
    "HttpUrlIntegrationProps",
    "WebSocketLambdaIntegration",
    "WebSocketMockIntegration",
]

publication.publish()

def _typecheckingstub__1051b1480a8cd47d711a84960fb401dc211dc0ba51fe7f789e2f339e045f4cca(
    id: builtins.str,
    listener: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationListener,
    *,
    method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
    parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
    secure_server_name: typing.Optional[builtins.str] = None,
    vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36449d0ed58756fe2f7fd192ea96aa9ea11f4987ffa1ac2965d2ab21b8270669(
    value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpConnectionType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5dc163e7b5e827e8fb331531e706af6b8aed694b5df252879219c3a88c32b21(
    value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22c266ae5ba72177fabe295e753bef793d5918f88d21c8d327d83f240cec5836(
    value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpIntegrationType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__131dd3859117b1c3dc8515c646fed00f9a95fe26870e5502a1c3005fbe9b464c(
    value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42f60194a638b05797e7ab331280416ee3fbd1b288d018b79a6abec4b2cd71b2(
    id: builtins.str,
    handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    *,
    parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
    payload_format_version: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a21cbac976f3b5b37bd0bba7a22ddc71aec8b09a5fa6bb1dacddf8c32e9f716(
    *,
    parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
    payload_format_version: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23538678538c3eeb8f55f23ba4c32b6153d35b1cb8bde3177648a1aa3f2dbf74(
    id: builtins.str,
    listener: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.INetworkListener,
    *,
    method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
    parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
    secure_server_name: typing.Optional[builtins.str] = None,
    vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e17455381dfbb8221af8a8b2fedb753c2c15627351dd4ea328f512f08c1b8aa(
    value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpConnectionType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e839b5ca71d9a12744874723d727aff24d662d22cb48e89b5c2079498a9ea169(
    value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dd29f9644934e9af4e806c5447a3f1b4a02bff13d0a48ec96e6841ab3feda06(
    value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpIntegrationType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9714bb1299b13b98b6badb1aeea61d4d940debe0b5ae0cfb9378612ba232941(
    value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af9150f33d84babdf3b7e860f41b0c38fa3a575b4c8540f59437e965167069aa(
    *,
    method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
    parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
    secure_server_name: typing.Optional[builtins.str] = None,
    vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00e34a738f2c9fe152b2ce2db7622b8c95db63b3e1b8768e2df2dd40d2776b14(
    id: builtins.str,
    service: _aws_cdk_aws_servicediscovery_ceddda9d.IService,
    *,
    method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
    parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
    secure_server_name: typing.Optional[builtins.str] = None,
    vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca1b680e984ff68c7d5229fa97abf6f06682d63c16b5f8eefd90b5b36a6f16e3(
    value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpConnectionType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdfe129511d17d3c6412bff75ad53162fb83e1d1846ad686c5e007d33bd43690(
    value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__098da7a8326a68b12492150350f132c4b8357f8c0cfdd6a1c04b9fbf3aed651b(
    value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpIntegrationType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__244bf7e00418063ee77d6ad97a4eb33851fd3d897cf6f5529a636591c85034e9(
    value: _aws_cdk_aws_apigatewayv2_alpha_050969fe.PayloadFormatVersion,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa07da47c0416387096e305b20d645f5184937633df8dd9d37d28f3a51f39610(
    *,
    method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
    parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
    secure_server_name: typing.Optional[builtins.str] = None,
    vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70de8f547e3566414a23dadeb1c53c9110bd6b7229aa282940328f686467e80e(
    id: builtins.str,
    url: builtins.str,
    *,
    method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
    parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__549a6c3540e3cf3d33b81f1183c39d8bc52fb71ae0bc3a6ac222f76c5f66ea70(
    *,
    method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
    parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__609e98b096947b613313989e0e2e6a2a72a4cc23b9ac8f7d5cd433c61249043a(
    id: builtins.str,
    handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69639dd59c40fb4ae670d012d6427385420cd2fb0351cc263cd8d27f49ed98b3(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee28cd43a256cf431e5012c28d37bdc89047f666d47217f86414c2a14605daf5(
    *,
    method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
    parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
    secure_server_name: typing.Optional[builtins.str] = None,
    vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18b50d7d30e6113bb374cb33044257c835e607dfbcfaf696fa3f6527d484232e(
    *,
    method: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.HttpMethod] = None,
    parameter_mapping: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.ParameterMapping] = None,
    secure_server_name: typing.Optional[builtins.str] = None,
    vpc_link: typing.Optional[_aws_cdk_aws_apigatewayv2_alpha_050969fe.IVpcLink] = None,
) -> None:
    """Type checking stubs"""
    pass
