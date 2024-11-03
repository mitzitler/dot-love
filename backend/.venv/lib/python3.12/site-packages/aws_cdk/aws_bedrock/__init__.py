'''
# Amazon Bedrock Construct Library

Amazon Bedrock is a fully managed service that offers a choice of foundation models (FMs)
along with a broad set of capabilities for building generative AI applications.

CloudFormation does not currently support any Bedrock resource types.
This construct library is a collection of constructs that can look up existing Bedrock models
for use with other services' CDK constructs, such as AWS Step Functions.

To look up a Bedrock base foundation model:

```python
import aws_cdk.aws_bedrock as bedrock


bedrock.FoundationModel.from_foundation_model_id(self, "Model", bedrock.FoundationModelIdentifier.ANTHROPIC_CLAUDE_V2)
```

To look up a Bedrock provisioned throughput model:

```python
import aws_cdk.aws_bedrock as bedrock


bedrock.ProvisionedModel.from_provisioned_model_arn(self, "Model", "arn:aws:bedrock:us-east-2:123456789012:provisioned-model/abc-123")
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

from .._jsii import *

import constructs as _constructs_77d1e7e8


class FoundationModelIdentifier(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_bedrock.FoundationModelIdentifier",
):
    '''The model identifiers for the Bedrock base foundation models.

    :see: https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_bedrock as bedrock
        
        
        bedrock.FoundationModel.from_foundation_model_id(self, "Model", bedrock.FoundationModelIdentifier.ANTHROPIC_CLAUDE_V2)
    '''

    def __init__(self, model_id: builtins.str) -> None:
        '''Constructor for foundation model identifier.

        :param model_id: the model identifier.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f232d69e34e8936af6b25fbb89b759790a47e68b671d931582f63554dd4bae52)
            check_type(argname="argument model_id", value=model_id, expected_type=type_hints["model_id"])
        jsii.create(self.__class__, self, [model_id])

    @jsii.python.classproperty
    @jsii.member(jsii_name="AI21_J2_GRANDE_INSTRUCT")
    def AI21_J2_GRANDE_INSTRUCT(cls) -> "FoundationModelIdentifier":
        '''Base model "ai21.j2-grande-instruct".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AI21_J2_GRANDE_INSTRUCT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AI21_J2_JUMBO_INSTRUCT")
    def AI21_J2_JUMBO_INSTRUCT(cls) -> "FoundationModelIdentifier":
        '''Base model "ai21.j2-jumbo-instruct".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AI21_J2_JUMBO_INSTRUCT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AI21_J2_MID")
    def AI21_J2_MID(cls) -> "FoundationModelIdentifier":
        '''Base model "ai21.j2-mid".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AI21_J2_MID"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AI21_J2_ULTRA")
    def AI21_J2_ULTRA(cls) -> "FoundationModelIdentifier":
        '''Base model "ai21.j2-ultra".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AI21_J2_ULTRA"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AI21_LABS_JURASSIC_2_MID_V1")
    def AI21_LABS_JURASSIC_2_MID_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "ai21.j2-mid-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AI21_LABS_JURASSIC_2_MID_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AI21_LABS_JURASSIC_2_ULTRA_V1")
    def AI21_LABS_JURASSIC_2_ULTRA_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "ai21.j2-ultra-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AI21_LABS_JURASSIC_2_ULTRA_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TITAN_EMBED_G1_TEXT_02")
    def AMAZON_TITAN_EMBED_G1_TEXT_02(cls) -> "FoundationModelIdentifier":
        '''Base model "amazon.titan-embed-g1-text-02".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AMAZON_TITAN_EMBED_G1_TEXT_02"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TITAN_EMBED_IMAGE_V1_0")
    def AMAZON_TITAN_EMBED_IMAGE_V1_0(cls) -> "FoundationModelIdentifier":
        '''Base model "amazon.titan-embed-image-v1:0".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AMAZON_TITAN_EMBED_IMAGE_V1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TITAN_EMBED_TEXT_V1_2_8K")
    def AMAZON_TITAN_EMBED_TEXT_V1_2_8_K(cls) -> "FoundationModelIdentifier":
        '''Base model "amazon.titan-embed-text-v1:2:8k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AMAZON_TITAN_EMBED_TEXT_V1_2_8K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TITAN_EMBEDDINGS_G1_TEXT_V1")
    def AMAZON_TITAN_EMBEDDINGS_G1_TEXT_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "amazon.titan-embed-text-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AMAZON_TITAN_EMBEDDINGS_G1_TEXT_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TITAN_IMAGE_GENERATOR_G1_V1")
    def AMAZON_TITAN_IMAGE_GENERATOR_G1_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "amazon.titan-image-generator-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AMAZON_TITAN_IMAGE_GENERATOR_G1_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TITAN_IMAGE_GENERATOR_V1_0")
    def AMAZON_TITAN_IMAGE_GENERATOR_V1_0(cls) -> "FoundationModelIdentifier":
        '''Base model "amazon.titan-image-generator-v1:0".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AMAZON_TITAN_IMAGE_GENERATOR_V1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TITAN_MULTIMODAL_EMBEDDINGS_G1_V1")
    def AMAZON_TITAN_MULTIMODAL_EMBEDDINGS_G1_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "amazon.titan-embed-image-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AMAZON_TITAN_MULTIMODAL_EMBEDDINGS_G1_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TITAN_TEXT_EXPRESS_V1_0_8K")
    def AMAZON_TITAN_TEXT_EXPRESS_V1_0_8_K(cls) -> "FoundationModelIdentifier":
        '''Base model "amazon.titan-text-express-v1:0:8k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AMAZON_TITAN_TEXT_EXPRESS_V1_0_8K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TITAN_TEXT_G1_EXPRESS_V1")
    def AMAZON_TITAN_TEXT_G1_EXPRESS_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "amazon.titan-text-express-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AMAZON_TITAN_TEXT_G1_EXPRESS_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TITAN_TEXT_LITE_V1")
    def AMAZON_TITAN_TEXT_LITE_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "amazon.titan-text-lite-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AMAZON_TITAN_TEXT_LITE_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TITAN_TEXT_LITE_V1_0_4K")
    def AMAZON_TITAN_TEXT_LITE_V1_0_4_K(cls) -> "FoundationModelIdentifier":
        '''Base model "amazon.titan-text-lite-v1:0:4k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AMAZON_TITAN_TEXT_LITE_V1_0_4K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_TITAN_TG1_LARGE")
    def AMAZON_TITAN_TG1_LARGE(cls) -> "FoundationModelIdentifier":
        '''Base model "amazon.titan-tg1-large".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "AMAZON_TITAN_TG1_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ANTHROPIC_CLAUDE_3_SONNET_20240229_V1_0")
    def ANTHROPIC_CLAUDE_3_SONNET_20240229_V1_0(cls) -> "FoundationModelIdentifier":
        '''Base model "anthropic.claude-3-sonnet-20240229-v1:0".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "ANTHROPIC_CLAUDE_3_SONNET_20240229_V1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ANTHROPIC_CLAUDE_INSTANT_V1")
    def ANTHROPIC_CLAUDE_INSTANT_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "anthropic.claude-instant-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "ANTHROPIC_CLAUDE_INSTANT_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ANTHROPIC_CLAUDE_INSTANT_V1_2_100K")
    def ANTHROPIC_CLAUDE_INSTANT_V1_2_100_K(cls) -> "FoundationModelIdentifier":
        '''Base model "anthropic.claude-instant-v1:2:100k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "ANTHROPIC_CLAUDE_INSTANT_V1_2_100K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ANTHROPIC_CLAUDE_V1")
    def ANTHROPIC_CLAUDE_V1(cls) -> "FoundationModelIdentifier":
        '''(deprecated) Base model "anthropic.claude-v1".

        :deprecated: use latest version of the model

        :stability: deprecated
        '''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "ANTHROPIC_CLAUDE_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ANTHROPIC_CLAUDE_V2")
    def ANTHROPIC_CLAUDE_V2(cls) -> "FoundationModelIdentifier":
        '''Base model "anthropic.claude-v2".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "ANTHROPIC_CLAUDE_V2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ANTHROPIC_CLAUDE_V2_0_100K")
    def ANTHROPIC_CLAUDE_V2_0_100_K(cls) -> "FoundationModelIdentifier":
        '''Base model "anthropic.claude-v2:0:100k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "ANTHROPIC_CLAUDE_V2_0_100K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ANTHROPIC_CLAUDE_V2_0_18K")
    def ANTHROPIC_CLAUDE_V2_0_18_K(cls) -> "FoundationModelIdentifier":
        '''Base model "anthropic.claude-v2:0:18k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "ANTHROPIC_CLAUDE_V2_0_18K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ANTHROPIC_CLAUDE_V2_1")
    def ANTHROPIC_CLAUDE_V2_1(cls) -> "FoundationModelIdentifier":
        '''Base model "anthropic.claude-v2:1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "ANTHROPIC_CLAUDE_V2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ANTHROPIC_CLAUDE_V2_1_18K")
    def ANTHROPIC_CLAUDE_V2_1_18_K(cls) -> "FoundationModelIdentifier":
        '''Base model "anthropic.claude-v2:1:18k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "ANTHROPIC_CLAUDE_V2_1_18K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ANTHROPIC_CLAUDE_V2_1_200K")
    def ANTHROPIC_CLAUDE_V2_1_200_K(cls) -> "FoundationModelIdentifier":
        '''Base model "anthropic.claude-v2:1:200k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "ANTHROPIC_CLAUDE_V2_1_200K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="COHERE_COMMAND_LIGHT_TEXT_V14_7_4K")
    def COHERE_COMMAND_LIGHT_TEXT_V14_7_4_K(cls) -> "FoundationModelIdentifier":
        '''Base model "cohere.command-light-text-v14:7:4k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "COHERE_COMMAND_LIGHT_TEXT_V14_7_4K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="COHERE_COMMAND_LIGHT_V14")
    def COHERE_COMMAND_LIGHT_V14(cls) -> "FoundationModelIdentifier":
        '''Base model "cohere.command-light-text-v14".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "COHERE_COMMAND_LIGHT_V14"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="COHERE_COMMAND_TEXT_V14_7_4K")
    def COHERE_COMMAND_TEXT_V14_7_4_K(cls) -> "FoundationModelIdentifier":
        '''Base model "cohere.command-text-v14:7:4k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "COHERE_COMMAND_TEXT_V14_7_4K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="COHERE_COMMAND_V14")
    def COHERE_COMMAND_V14(cls) -> "FoundationModelIdentifier":
        '''Base model "cohere.command-text-v14".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "COHERE_COMMAND_V14"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="COHERE_EMBED_ENGLISH_V3")
    def COHERE_EMBED_ENGLISH_V3(cls) -> "FoundationModelIdentifier":
        '''Base model "cohere.embed-english-v3".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "COHERE_EMBED_ENGLISH_V3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="COHERE_EMBED_MULTILINGUAL_V3")
    def COHERE_EMBED_MULTILINGUAL_V3(cls) -> "FoundationModelIdentifier":
        '''Base model "cohere.embed-multilingual-v3".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "COHERE_EMBED_MULTILINGUAL_V3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_LLAMA_2_13B_CHAT_V1_0_4K")
    def META_LLAMA_2_13_B_CHAT_V1_0_4_K(cls) -> "FoundationModelIdentifier":
        '''Base model "meta.llama2-13b-chat-v1:0:4k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "META_LLAMA_2_13B_CHAT_V1_0_4K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_LLAMA_2_13B_V1")
    def META_LLAMA_2_13_B_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "meta.llama2-13b-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "META_LLAMA_2_13B_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_LLAMA_2_13B_V1_0_4K")
    def META_LLAMA_2_13_B_V1_0_4_K(cls) -> "FoundationModelIdentifier":
        '''Base model "meta.llama2-13b-v1:0:4k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "META_LLAMA_2_13B_V1_0_4K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_LLAMA_2_70B_CHAT_V1_0_4K")
    def META_LLAMA_2_70_B_CHAT_V1_0_4_K(cls) -> "FoundationModelIdentifier":
        '''Base model "meta.llama2-70b-chat-v1:0:4k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "META_LLAMA_2_70B_CHAT_V1_0_4K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_LLAMA_2_70B_V1")
    def META_LLAMA_2_70_B_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "meta.llama2-70b-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "META_LLAMA_2_70B_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_LLAMA_2_70B_V1_0_4K")
    def META_LLAMA_2_70_B_V1_0_4_K(cls) -> "FoundationModelIdentifier":
        '''Base model "meta.llama2-70b-v1:0:4k".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "META_LLAMA_2_70B_V1_0_4K"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_LLAMA_2_CHAT_13B_V1")
    def META_LLAMA_2_CHAT_13_B_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "meta.llama2-13b-chat-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "META_LLAMA_2_CHAT_13B_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="META_LLAMA_2_CHAT_70B_V1")
    def META_LLAMA_2_CHAT_70_B_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "meta.llama2-70b-chat-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "META_LLAMA_2_CHAT_70B_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MISTRAL_MISTRAL_7B_INSTRUCT_V0_2")
    def MISTRAL_MISTRAL_7_B_INSTRUCT_V0_2(cls) -> "FoundationModelIdentifier":
        '''Base model "mistral.mistral-7b-instruct-v0:2".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "MISTRAL_MISTRAL_7B_INSTRUCT_V0_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MISTRAL_MIXTRAL_8X7B_INSTRUCT_V0_1")
    def MISTRAL_MIXTRAL_8_X7_B_INSTRUCT_V0_1(cls) -> "FoundationModelIdentifier":
        '''Base model "mistral.mixtral-8x7b-instruct-v0:1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "MISTRAL_MIXTRAL_8X7B_INSTRUCT_V0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="STABILITY_STABLE_DIFFUSION_XL")
    def STABILITY_STABLE_DIFFUSION_XL(cls) -> "FoundationModelIdentifier":
        '''(deprecated) Base model "stability.stable-diffusion-xl".

        :deprecated: use latest version of the model

        :stability: deprecated
        '''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "STABILITY_STABLE_DIFFUSION_XL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="STABILITY_STABLE_DIFFUSION_XL_V0")
    def STABILITY_STABLE_DIFFUSION_XL_V0(cls) -> "FoundationModelIdentifier":
        '''(deprecated) Base model "stability.stable-diffusion-xl-v0".

        :deprecated: use latest version of the model

        :stability: deprecated
        '''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "STABILITY_STABLE_DIFFUSION_XL_V0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="STABILITY_STABLE_DIFFUSION_XL_V1")
    def STABILITY_STABLE_DIFFUSION_XL_V1(cls) -> "FoundationModelIdentifier":
        '''Base model "stability.stable-diffusion-xl-v1".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "STABILITY_STABLE_DIFFUSION_XL_V1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="STABILITY_STABLE_DIFFUSION_XL_V1_0")
    def STABILITY_STABLE_DIFFUSION_XL_V1_0(cls) -> "FoundationModelIdentifier":
        '''Base model "stability.stable-diffusion-xl-v1:0".'''
        return typing.cast("FoundationModelIdentifier", jsii.sget(cls, "STABILITY_STABLE_DIFFUSION_XL_V1_0"))

    @builtins.property
    @jsii.member(jsii_name="modelId")
    def model_id(self) -> builtins.str:
        '''the model identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "modelId"))


@jsii.interface(jsii_type="aws-cdk-lib.aws_bedrock.IModel")
class IModel(typing_extensions.Protocol):
    '''Represents a Bedrock model.

    The model could be a foundation model, a custom model, or a provisioned model.
    '''

    @builtins.property
    @jsii.member(jsii_name="modelArn")
    def model_arn(self) -> builtins.str:
        '''The ARN of the model.

        :see: https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonbedrock.html#amazonbedrock-actions-as-permissions
        '''
        ...


class _IModelProxy:
    '''Represents a Bedrock model.

    The model could be a foundation model, a custom model, or a provisioned model.
    '''

    __jsii_type__: typing.ClassVar[str] = "aws-cdk-lib.aws_bedrock.IModel"

    @builtins.property
    @jsii.member(jsii_name="modelArn")
    def model_arn(self) -> builtins.str:
        '''The ARN of the model.

        :see: https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonbedrock.html#amazonbedrock-actions-as-permissions
        '''
        return typing.cast(builtins.str, jsii.get(self, "modelArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IModel).__jsii_proxy_class__ = lambda : _IModelProxy


@jsii.implements(IModel)
class ProvisionedModel(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_bedrock.ProvisionedModel",
):
    '''A Bedrock provisioned model.

    Note: CloudFormation does not currently support creating Bedrock Provisioned Throughput
    resources outside of a custom resource. You can import provisioned models created by
    provisioning throughput in Bedrock outside the CDK or via a custom resource with
    {@link ProvisionedModel#fromProvisionedModelArn }.

    :see: https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_bedrock as bedrock
        
        
        bedrock.ProvisionedModel.from_provisioned_model_arn(self, "Model", "arn:aws:bedrock:us-east-2:123456789012:provisioned-model/abc-123")
    '''

    @jsii.member(jsii_name="fromProvisionedModelArn")
    @builtins.classmethod
    def from_provisioned_model_arn(
        cls,
        _scope: _constructs_77d1e7e8.Construct,
        _id: builtins.str,
        provisioned_model_arn: builtins.str,
    ) -> IModel:
        '''Import an provisioned model given an ARN.

        :param _scope: -
        :param _id: -
        :param provisioned_model_arn: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__729a89649bbbe97643ef676e5c7a3debb583fa04ca31db203a85e9e6631bd8eb)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
            check_type(argname="argument _id", value=_id, expected_type=type_hints["_id"])
            check_type(argname="argument provisioned_model_arn", value=provisioned_model_arn, expected_type=type_hints["provisioned_model_arn"])
        return typing.cast(IModel, jsii.sinvoke(cls, "fromProvisionedModelArn", [_scope, _id, provisioned_model_arn]))

    @builtins.property
    @jsii.member(jsii_name="modelArn")
    def model_arn(self) -> builtins.str:
        '''The ARN of the provisioned model.'''
        return typing.cast(builtins.str, jsii.get(self, "modelArn"))


@jsii.implements(IModel)
class FoundationModel(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_bedrock.FoundationModel",
):
    '''A Bedrock base foundation model.

    :see: https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_bedrock as bedrock
        
        
        bedrock.FoundationModel.from_foundation_model_id(self, "Model", bedrock.FoundationModelIdentifier.ANTHROPIC_CLAUDE_V2)
    '''

    @jsii.member(jsii_name="fromFoundationModelId")
    @builtins.classmethod
    def from_foundation_model_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        _id: builtins.str,
        foundation_model_id: FoundationModelIdentifier,
    ) -> "FoundationModel":
        '''Construct a Bedrock base foundation model given the model identifier.

        :param scope: The parent construct.
        :param _id: The name of the model construct.
        :param foundation_model_id: The model identifier such as 'amazon.titan-text-express-v1'.

        :return: A Bedrock base foundation model.

        :see: https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids-arns.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f64541c2daf01636476388a49436a79864b7cc8c00bbbf47f4d0f84ccbf0ec56)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument _id", value=_id, expected_type=type_hints["_id"])
            check_type(argname="argument foundation_model_id", value=foundation_model_id, expected_type=type_hints["foundation_model_id"])
        return typing.cast("FoundationModel", jsii.sinvoke(cls, "fromFoundationModelId", [scope, _id, foundation_model_id]))

    @builtins.property
    @jsii.member(jsii_name="modelArn")
    def model_arn(self) -> builtins.str:
        '''The foundation model ARN.'''
        return typing.cast(builtins.str, jsii.get(self, "modelArn"))

    @builtins.property
    @jsii.member(jsii_name="modelId")
    def model_id(self) -> builtins.str:
        '''The foundation model ID.

        Example::

            "amazon.titan-text-express-v1"
        '''
        return typing.cast(builtins.str, jsii.get(self, "modelId"))


__all__ = [
    "FoundationModel",
    "FoundationModelIdentifier",
    "IModel",
    "ProvisionedModel",
]

publication.publish()

def _typecheckingstub__f232d69e34e8936af6b25fbb89b759790a47e68b671d931582f63554dd4bae52(
    model_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__729a89649bbbe97643ef676e5c7a3debb583fa04ca31db203a85e9e6631bd8eb(
    _scope: _constructs_77d1e7e8.Construct,
    _id: builtins.str,
    provisioned_model_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f64541c2daf01636476388a49436a79864b7cc8c00bbbf47f4d0f84ccbf0ec56(
    scope: _constructs_77d1e7e8.Construct,
    _id: builtins.str,
    foundation_model_id: FoundationModelIdentifier,
) -> None:
    """Type checking stubs"""
    pass
