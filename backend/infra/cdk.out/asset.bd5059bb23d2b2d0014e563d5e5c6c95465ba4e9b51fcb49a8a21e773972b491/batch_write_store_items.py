import os
import boto3

########################################################
# Setup
########################################################
dynamodb = boto3.resource("dynamodb")
COMMODITY_TABLE_NAME = os.environ["commodity_table_name"]
table = dynamodb.Table(COMMODITY_TABLE_NAME)
CW_STORE_ITEMS = [
    {
        "product_name": "save the attendants shirt",
        "price": 2500,
        "product_type": "clothing",
        "quantity": 50,
    },
    {
        "product_name": "magwadi shirt",
        "price": 2500,
        "product_type": "clothing",
        "quantity": 50,
    },
    {
        "product_name": "quuarux earrings",
        "price": 3000,
        "product_type": "art",
        "quantity": 50,
    },
    {
        "product_name": "pamphlet bundle",
        "price": 1000,
        "product_type": "art",
        "quantity": 50,
    },
    {
        "product_name": "quuarux gas wars shirt",
        "price": 2500,
        "product_type": "clothing",
        "quantity": 50,
    },
    {
        "product_name": "enter car world shirt",
        "price": 2500,
        "product_type": "clothing",
        "quantity": 50,
    },
    {
        "product_name": "enter car world poster",
        "price": 3000,
        "product_type": "art",
        "quantity": 50,
    },
    {
        "product_name": "tat pass bracelet",
        "price": 6500,
        "product_type": "art",
        "quantity": 50,
    },
    {
        "product_name": "the artifact",
        "price": 800000,
        "product_type": "art",
        "quantity": 50,
    },
    {
        "product_name": "vip pas",
        "price": 1200,
        "product_type": "art",
        "quantity": 50,
    },
    {
        "product_name": "attendant pendant",
        "price": 2500,
        "product_type": "art",
        "quantity": 50,
    },
    {
        "product_name": "devotion point",
        "price": 100,
        "product_type": "art",
        "quantity": 50,
    },
    {
        "product_name": "william banks devotional candle",
        "price": 1200,
        "product_type": "art",
        "quantity": 50,
    },
    {
        "product_name": "car world water",
        "price": 500,
        "product_type": "art",
        "quantity": 50,
    },
    {
        "product_name": "car world emblem earrings",
        "price": 2500,
        "product_type": "art",
        "quantity": 50,
    },
    {
        "product_name": "car world supper book",
        "price": 1000,
        "product_type": "art",
        "quantity": 50,
    },
    {
        "product_name": "car world supper book 10 pack",
        "price": 7000,
        "product_type": "art",
        "quantity": 50,
    },
]


########################################################
# Lambda Handler
########################################################
def handler(event, context):
    with table.batch_writer() as batch:
        for commodity in CW_STORE_ITEMS:
            if commodity["product_type"] == "clothing":
                # Handle sizing for clothing
                for size in ["xs", "s", "m", "l", "xl"]:
                    clothing_commodity = dict(commodity)
                    clothing_commodity[
                        "product_name"
                    ] = f'{commodity["product_name"]}_{size}'
                    batch.put_item(Item=clothing_commodity)
            else:
                batch.put_item(Item=commodity)

    return
