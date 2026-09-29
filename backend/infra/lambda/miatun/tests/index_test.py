import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Set required environment variables before importing index
os.environ["user_table_name"] = "test_user_table"
os.environ["registry_item_table_name"] = "test_registry_item_table"
os.environ["registry_claim_table_name"] = "test_registry_claim_table"
os.environ["letters_table_name"] = "test_letters_table"
os.environ["letters_disjoined_pairs_table_name"] = "test_letters_disjoined_pairs_table"
os.environ["internal_api_key"] = "test_internal_key"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Add parent directory to path to import the lambda function
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock boto3 before importing index to avoid AWS credentials requirement
with patch("boto3.client"):
    import index


########################################################
# Deserialized-dict builders, for exercising build_letter_records() directly
########################################################
def make_item(item_id, item_name, claimant_id="", brand="", price_cents=None):
    item = {
        "id": item_id,
        "item_name": item_name,
        "brand": brand,
        "claimant_id": claimant_id,
        "received": True,
    }
    if price_cents is not None:
        item["price_cents"] = price_cents
    return item


def make_claim(item_id, claimant_id, claim_state="CLAIMED"):
    return {
        "id": f"claim-{item_id}-{claimant_id}",
        "item_id": item_id,
        "claimant_id": claimant_id,
        "claim_state": claim_state,
    }


def make_user(first_last, pair="", **contact):
    user = {
        "first_last": first_last,
        "guest_pair_first_last": pair,
        "phone": "+15555550100",
        "street": "123 Main St",
        "second_line": "Apt 4",
        "city": "Brooklyn",
        "state_loc": "NY",
        "zipcode": "11201",
        "country": "USA",
    }
    user.update(contact)
    return user


########################################################
# Raw DynamoDB-typed helpers, for seeding FakeDynamoDB tables
########################################################
def to_dynamo_value(value):
    """Recursively convert a plain Python value into a raw DynamoDB-typed
    value (the same shape TypeDeserializer/CWDynamoClient produce/consume),
    including nested lists-of-maps like the `gifts` field."""
    if value is None:
        return {"NULL": True}
    if isinstance(value, bool):
        return {"BOOL": value}
    if isinstance(value, (int, float)):
        return {"N": str(value)}
    if isinstance(value, dict):
        return {"M": {k: to_dynamo_value(v) for k, v in value.items()}}
    if isinstance(value, list):
        return {"L": [to_dynamo_value(v) for v in value]}
    return {"S": str(value)}


def make_raw_item(item_id, item_name, claimant_id="", brand="", price_cents=None, received=True):
    item = {
        "id": {"S": item_id},
        "item_name": {"S": item_name},
        "brand": {"S": brand},
        "claimant_id": {"S": claimant_id},
        "received": {"BOOL": received},
    }
    if price_cents is not None:
        item["price_cents"] = {"N": str(price_cents)}
    return item


def make_raw_claim(claim_id, item_id, claimant_id, claim_state="CLAIMED"):
    return {
        "id": {"S": claim_id},
        "item_id": {"S": item_id},
        "claimant_id": {"S": claimant_id},
        "claim_state": {"S": claim_state},
    }


def make_raw_user(first_last, pair="", **contact):
    fields = {
        "phone": "+15555550100",
        "street": "123 Main St",
        "second_line": "Apt 4",
        "city": "Brooklyn",
        "state_loc": "NY",
        "zipcode": "11201",
        "country": "USA",
    }
    fields.update(contact)
    raw = {"first_last": {"S": first_last}, "guest_pair_first_last": {"S": pair}}
    for key, value in fields.items():
        raw[key] = {"S": value}
    return raw


def make_raw_letter(letter_id, gifts=None, **fields):
    raw = {"id": {"S": letter_id}}
    defaults = {
        "guest": "",
        "partner": "",
        "claimant_id": "",
        "phone": "",
        "street": "",
        "second_line": "",
        "city": "",
        "state_loc": "",
        "zipcode": "",
        "country": "",
        "letter_body": "",
        "status": "DRAFT",
        "source": "SYNC",
    }
    defaults.update(fields)
    for key, value in defaults.items():
        raw[key] = {"S": value}
    raw["gifts"] = to_dynamo_value(gifts if gifts is not None else [])
    return raw


class FakeDynamoDB:
    """Minimal in-memory double for CWDynamoClient — just enough behavior
    (get/get_all/update/delete/batch_get_items) to exercise real upsert
    semantics (e.g. sync never clobbering a written letter body) without
    touching real AWS."""

    def __init__(self):
        self.tables = {}  # table_name -> {id: raw dynamo-typed item}

    def _table(self, table_name):
        return self.tables.setdefault(table_name, {})

    @staticmethod
    def _key_value(key_expression):
        """Extract the single partition-key value regardless of its
        attribute name ("id" for letters/disjoined-pairs, "first_last" for
        users, etc.) — real DynamoDB Key dicts aren't hardcoded to "id"."""
        ((_, value),) = key_expression.items()
        return value["S"]

    def get(self, table_name, key_expression):
        return self._table(table_name).get(self._key_value(key_expression))

    def get_all(self, table_name, filter_expression=None, expression_attribute_values=None):
        return list(self._table(table_name).values())

    def batch_get_items(self, table_name, keys, projection_expression=None):
        table = self._table(table_name)
        return [
            table[key["first_last"]["S"]]
            for key in keys
            if key["first_last"]["S"] in table
        ]

    def update(self, table_name, key_expression, field_value_map, manual_expression_attribute_map=None):
        table = self._table(table_name)
        item_id = self._key_value(key_expression)
        existing = table.get(item_id, dict(key_expression))
        for field_name, field_value in field_value_map.items():
            existing[field_name] = to_dynamo_value(field_value)
        table[item_id] = existing
        return {}

    def delete(self, table_name, key_expression):
        self._table(table_name).pop(self._key_value(key_expression), None)
        return {}


class TestHelpers(unittest.TestCase):
    """Test suite for formatting helpers."""

    def test_title_case_first_last(self):
        self.assertEqual(index.title_case_first_last("john_smith"), "John Smith")

    def test_title_case_single_token(self):
        self.assertEqual(index.title_case_first_last("plus_one"), "Plus One")
        self.assertEqual(index.title_case_first_last("cher"), "Cher")

    def test_title_case_empty(self):
        self.assertEqual(index.title_case_first_last(""), "")
        self.assertEqual(index.title_case_first_last(None), "")


class TestBuildLetterRecords(unittest.TestCase):
    """Test suite for the claims/items/users join + household-grouping logic."""

    def test_full_record_with_partner(self):
        items = {"i1": make_item("i1", "Stand Mixer", brand="KitchenAid", price_cents=44999)}
        claims = [make_claim("i1", "john_smith")]
        users = {"john_smith": make_user("john_smith", pair="jane_smith")}

        letters = index.build_letter_records(items, claims, users)

        self.assertEqual(len(letters), 1)
        letter = letters[0]
        self.assertEqual(letter.id, "couple:jane_smith|john_smith")
        self.assertEqual(letter.guest, "John Smith")
        self.assertEqual(letter.partner, "Jane Smith")
        self.assertEqual(len(letter.gifts), 1)
        self.assertEqual(letter.gifts[0]["gift"], "Stand Mixer")
        self.assertEqual(letter.gifts[0]["brand"], "KitchenAid")
        self.assertEqual(letter.gifts[0]["price_cents"], 44999)
        self.assertEqual(letter.phone, "+15555550100")
        self.assertEqual(letter.street, "123 Main St")
        self.assertEqual(letter.city, "Brooklyn")
        self.assertEqual(letter.status, index.LetterStatus.DRAFT)
        self.assertEqual(letter.letter_body, "")
        self.assertEqual(letter.source, "SYNC")

    def test_guest_with_multiple_gifts_merged_into_one_letter(self):
        items = {
            "i1": make_item("i1", "Toaster"),
            "i2": make_item("i2", "Blender"),
        }
        claims = [
            make_claim("i1", "john_smith"),
            make_claim("i2", "john_smith"),
        ]

        letters = index.build_letter_records(items, claims, {})

        self.assertEqual(len(letters), 1)
        letter = letters[0]
        self.assertEqual(letter.id, "guest:john_smith")
        self.assertEqual(letter.guest, "John Smith")
        self.assertEqual(len(letter.gifts), 2)
        self.assertEqual(
            sorted(g["gift"] for g in letter.gifts), ["Blender", "Toaster"]
        )

    def test_couple_each_claiming_a_gift_merged_into_one_letter(self):
        items = {
            "i1": make_item("i1", "Toaster"),
            "i2": make_item("i2", "Blender"),
        }
        claims = [
            make_claim("i1", "john_smith"),
            make_claim("i2", "jane_smith"),
        ]
        users = {
            "john_smith": make_user("john_smith", pair="jane_smith"),
            "jane_smith": make_user("jane_smith", pair="john_smith"),
        }

        letters = index.build_letter_records(items, claims, users)

        self.assertEqual(len(letters), 1)
        letter = letters[0]
        self.assertEqual(letter.id, "couple:jane_smith|john_smith")
        # primary claimant is whichever id sorts first, alphabetically
        self.assertEqual(letter.guest, "Jane Smith")
        self.assertEqual(letter.partner, "John Smith")
        self.assertEqual(len(letter.gifts), 2)
        self.assertEqual(
            sorted(g["gift"] for g in letter.gifts), ["Blender", "Toaster"]
        )

    def test_couple_grouping_is_order_independent(self):
        """It shouldn't matter which partner's identity claimed a gift —
        it still lands in the same household letter as the other partner's
        gifts."""
        items_a = {"i1": make_item("i1", "Toaster")}
        claims_a = [make_claim("i1", "jane_smith")]
        users_a = {"jane_smith": make_user("jane_smith", pair="john_smith")}
        letters_a = index.build_letter_records(items_a, claims_a, users_a)

        items_b = {"i1": make_item("i1", "Toaster")}
        claims_b = [make_claim("i1", "john_smith")]
        users_b = {"john_smith": make_user("john_smith", pair="jane_smith")}
        letters_b = index.build_letter_records(items_b, claims_b, users_b)

        self.assertEqual(letters_a[0].id, letters_b[0].id)

    def test_claim_for_non_received_item_excluded(self):
        items = {}  # nothing received
        claims = [make_claim("i1", "john_smith")]

        letters = index.build_letter_records(items, claims, {})

        self.assertEqual(letters, [])

    def test_unclaimed_claim_state_excluded(self):
        items = {"i1": make_item("i1", "Vase")}
        claims = [make_claim("i1", "john_smith", claim_state="UNCLAIMED")]

        letters = index.build_letter_records(items, claims, {})

        # The UNCLAIMED claim is skipped, but the received item still appears
        # via the fallback (using the item's own claimant_id, blank here).
        # With no identifiable claimant, it gets its own letter keyed by
        # the item's id rather than being grouped.
        self.assertEqual(len(letters), 1)
        self.assertEqual(letters[0].guest, "")
        self.assertEqual(letters[0].id, "item:i1")

    def test_purchased_claim_state_included(self):
        items = {"i1": make_item("i1", "Vase")}
        claims = [make_claim("i1", "john_smith", claim_state="PURCHASED")]

        letters = index.build_letter_records(items, claims, {})

        self.assertEqual(len(letters), 1)
        self.assertEqual(letters[0].guest, "John Smith")
        self.assertEqual(letters[0].id, "guest:john_smith")

    def test_claimant_missing_from_users_table(self):
        items = {"i1": make_item("i1", "Blender")}
        claims = [make_claim("i1", "plus_one")]

        letters = index.build_letter_records(items, claims, {})

        self.assertEqual(len(letters), 1)
        self.assertEqual(letters[0].guest, "Plus One")
        self.assertEqual(letters[0].partner, "")
        self.assertEqual(letters[0].phone, "")
        self.assertEqual(letters[0].street, "")
        self.assertEqual(letters[0].id, "guest:plus_one")

    def test_duplicate_claims_deduped(self):
        items = {"i1": make_item("i1", "Toaster")}
        claims = [
            make_claim("i1", "john_smith"),
            make_claim("i1", "john_smith", claim_state="PURCHASED"),
        ]

        letters = index.build_letter_records(items, claims, {})

        self.assertEqual(len(letters), 1)
        self.assertEqual(len(letters[0].gifts), 1)

    def test_received_item_without_claim_falls_back_to_item_claimant(self):
        items = {"i1": make_item("i1", "Wok", claimant_id="amy_pond")}
        users = {"amy_pond": make_user("amy_pond")}

        letters = index.build_letter_records(items, [], users)

        self.assertEqual(len(letters), 1)
        self.assertEqual(letters[0].guest, "Amy Pond")
        self.assertEqual(letters[0].phone, "+15555550100")
        self.assertEqual(letters[0].id, "guest:amy_pond")

    def test_records_sorted_by_guest(self):
        items = {
            "i1": make_item("i1", "Zester"),
            "i2": make_item("i2", "Apron"),
            "i3": make_item("i3", "Kettle"),
        }
        claims = [
            make_claim("i1", "zoe_washburne"),
            make_claim("i2", "amy_pond"),
            make_claim("i3", "amy_pond"),
        ]

        letters = index.build_letter_records(items, claims, {})

        self.assertEqual([letter.guest for letter in letters], ["Amy Pond", "Zoe Washburne"])
        amy_letter = letters[0]
        self.assertEqual(len(amy_letter.gifts), 2)
        self.assertEqual(
            sorted(g["gift"] for g in amy_letter.gifts), ["Apron", "Kettle"]
        )

    def test_disjoined_pair_produces_two_guest_letters(self):
        items = {
            "i1": make_item("i1", "Toaster"),
            "i2": make_item("i2", "Blender"),
        }
        claims = [
            make_claim("i1", "john_smith"),
            make_claim("i2", "jane_smith"),
        ]
        users = {
            "john_smith": make_user("john_smith", pair="jane_smith"),
            "jane_smith": make_user("jane_smith", pair="john_smith"),
        }

        letters = index.build_letter_records(
            items, claims, users,
            disjoined_pair_keys={"jane_smith|john_smith"},
        )

        self.assertEqual(len(letters), 2)
        by_id = {letter.id: letter for letter in letters}
        self.assertIn("guest:john_smith", by_id)
        self.assertIn("guest:jane_smith", by_id)
        self.assertEqual(by_id["guest:john_smith"].partner, "")
        self.assertEqual(by_id["guest:jane_smith"].partner, "")
        self.assertEqual([g["gift"] for g in by_id["guest:john_smith"].gifts], ["Toaster"])
        self.assertEqual([g["gift"] for g in by_id["guest:jane_smith"].gifts], ["Blender"])

    def test_disjoined_pair_keys_omitted_is_backward_compatible(self):
        """Calling build_letter_records with no 4th argument (the pre-disjoin
        signature) must behave exactly as before — couples still merge."""
        items = {"i1": make_item("i1", "Stand Mixer", brand="KitchenAid", price_cents=44999)}
        claims = [make_claim("i1", "john_smith")]
        users = {"john_smith": make_user("john_smith", pair="jane_smith")}

        letters = index.build_letter_records(items, claims, users)

        self.assertEqual(len(letters), 1)
        self.assertEqual(letters[0].id, "couple:jane_smith|john_smith")
        self.assertEqual(letters[0].partner, "Jane Smith")


class TestSyncPreservesLetterBody(unittest.TestCase):
    """The claims-sync upsert must never clobber a letter body/status that's
    already been written, even after the source claims data is re-synced."""

    def setUp(self):
        self.fake_db = FakeDynamoDB()
        self.fake_db.tables[index.REGISTRY_ITEM_TABLE_NAME] = {
            "i1": make_raw_item("i1", "Stand Mixer", claimant_id="john_smith", brand="KitchenAid", price_cents=44999)
        }
        self.fake_db.tables[index.REGISTRY_CLAIM_TABLE_NAME] = {
            "c1": make_raw_claim("c1", "i1", "john_smith", claim_state="PURCHASED")
        }
        self.fake_db.tables[index.USER_TABLE_NAME] = {
            "john_smith": make_raw_user("john_smith", pair="jane_smith")
        }

    def run_sync(self):
        received_items_by_id, claims, users_by_first_last, disjoined_pair_keys = (
            index.fetch_sync_data(self.fake_db)
        )
        letters = index.build_letter_records(
            received_items_by_id,
            claims,
            users_by_first_last,
            disjoined_pair_keys=disjoined_pair_keys,
        )
        for letter in letters:
            letter.sync_upsert_db(self.fake_db)
        return letters

    def test_second_sync_preserves_edited_body_and_status(self):
        letters = self.run_sync()
        self.assertEqual(len(letters), 1)
        letter_id = letters[0].id
        self.assertEqual(letter_id, "couple:jane_smith|john_smith")

        # Admin opens the letter, writes the body, and marks it WRITTEN
        letter = index.LetterRecord.from_letter_id_db(letter_id, self.fake_db)
        letter.letter_body = "Dear John, thank you so much for the mixer!"
        letter.status = index.LetterStatus.WRITTEN
        letter.update_db(self.fake_db)

        # Re-running sync (e.g. because a new gift was received) must not
        # touch this letter's body/status
        self.run_sync()

        reloaded = index.LetterRecord.from_letter_id_db(letter_id, self.fake_db)
        self.assertEqual(reloaded.letter_body, "Dear John, thank you so much for the mixer!")
        self.assertEqual(reloaded.status, index.LetterStatus.WRITTEN)
        # contact/gift fields still reflect the latest sync
        self.assertEqual(reloaded.guest, "John Smith")
        self.assertEqual(reloaded.source, "SYNC")
        self.assertEqual(len(reloaded.gifts), 1)


class TestAPIEndpoints(unittest.TestCase):
    """Test suite for the API routes through the full handler."""

    @staticmethod
    def make_event(path, method="GET", headers=None, body=None):
        event = {
            "version": "2.0",
            "rawPath": path,
            "rawQueryString": "",
            "headers": headers or {},
            "requestContext": {
                "http": {"method": method, "path": path, "sourceIp": "127.0.0.1"},
                "requestId": "test-request-id",
                "stage": "$default",
            },
            "isBase64Encoded": False,
        }
        if body is not None:
            event["body"] = json.dumps(body)
        return event

    @staticmethod
    def make_context():
        ctx = MagicMock()
        ctx.function_name = "miatun"
        ctx.memory_limit_in_mb = 512
        ctx.invoked_function_arn = (
            "arn:aws:lambda:us-east-1:123456789012:function:miatun"
        )
        ctx.aws_request_id = "test-aws-request-id"
        return ctx

    def setUp(self):
        self.fake_db = FakeDynamoDB()
        self.auth_headers = {"Internal-Api-Key": "test_internal_key"}

    def test_ping_no_headers_required(self):
        response = index.handler(self.make_event("/miatun/ping"), self.make_context())
        self.assertEqual(response["statusCode"], 200)

    def test_sync_rejects_missing_api_key(self):
        event = self.make_event("/miatun/sync", method="POST")
        response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 401)

    def test_sync_rejects_wrong_api_key(self):
        event = self.make_event(
            "/miatun/sync", method="POST", headers={"internal-api-key": "wrong"}
        )
        response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 401)

    def test_sync_success(self):
        self.fake_db.tables[index.REGISTRY_ITEM_TABLE_NAME] = {
            "i1": make_raw_item("i1", "Stand Mixer", claimant_id="john_smith", brand="KitchenAid", price_cents=44999)
        }
        self.fake_db.tables[index.REGISTRY_CLAIM_TABLE_NAME] = {
            "c1": make_raw_claim("c1", "i1", "john_smith", claim_state="PURCHASED")
        }
        self.fake_db.tables[index.USER_TABLE_NAME] = {
            "john_smith": make_raw_user("john_smith", pair="jane_smith")
        }

        event = self.make_event("/miatun/sync", method="POST", headers=self.auth_headers)
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["message"], "sync success")
        self.assertEqual(body["synced_count"], 1)

        letter = index.LetterRecord.from_letter_id_db("couple:jane_smith|john_smith", self.fake_db)
        self.assertIsNotNone(letter)
        self.assertEqual(letter.guest, "John Smith")
        self.assertEqual(letter.status, index.LetterStatus.DRAFT)
        self.assertEqual(letter.letter_body, "")
        self.assertEqual(len(letter.gifts), 1)

    def test_sync_merges_couple_and_multi_gift_guest_each_into_one_letter(self):
        self.fake_db.tables[index.REGISTRY_ITEM_TABLE_NAME] = {
            "i1": make_raw_item("i1", "Toaster"),
            "i2": make_raw_item("i2", "Blender"),
            "i3": make_raw_item("i3", "Kettle"),
        }
        self.fake_db.tables[index.REGISTRY_CLAIM_TABLE_NAME] = {
            "c1": make_raw_claim("c1", "i1", "john_smith"),
            "c2": make_raw_claim("c2", "i2", "jane_smith"),
            "c3": make_raw_claim("c3", "i3", "amy_pond"),
        }
        self.fake_db.tables[index.USER_TABLE_NAME] = {
            "john_smith": make_raw_user("john_smith", pair="jane_smith"),
            "jane_smith": make_raw_user("jane_smith", pair="john_smith"),
            "amy_pond": make_raw_user("amy_pond"),
        }

        event = self.make_event("/miatun/sync", method="POST", headers=self.auth_headers)
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        # one letter for the couple (2 gifts) + one for the solo guest (1 gift)
        self.assertEqual(body["synced_count"], 2)

        letters = index.LetterRecord.get_all_letters_db(self.fake_db)
        by_id = {letter.id: letter for letter in letters}
        self.assertEqual(len(letters), 2)
        self.assertEqual(len(by_id["couple:jane_smith|john_smith"].gifts), 2)
        self.assertEqual(len(by_id["guest:amy_pond"].gifts), 1)

    def test_sync_prunes_stale_sync_letters_but_keeps_manual(self):
        self.fake_db.tables[index.REGISTRY_ITEM_TABLE_NAME] = {
            "i1": make_raw_item("i1", "Toaster", claimant_id="john_smith"),
        }
        self.fake_db.tables[index.REGISTRY_CLAIM_TABLE_NAME] = {
            "c1": make_raw_claim("c1", "i1", "john_smith"),
        }
        self.fake_db.tables[index.USER_TABLE_NAME] = {
            "john_smith": make_raw_user("john_smith"),
        }
        # Seed a stale SYNC letter (e.g. left over from before the household
        # grouping change) and a MANUAL letter that must survive pruning.
        self.fake_db.tables[index.LETTERS_TABLE_NAME] = {
            "stale-sync-id": make_raw_letter("stale-sync-id", source="SYNC", guest="Old Stale"),
            "manual-id": make_raw_letter("manual-id", source="MANUAL", guest="Hand Entered"),
        }

        event = self.make_event("/miatun/sync", method="POST", headers=self.auth_headers)
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["pruned_count"], 1)

        remaining_ids = set(self.fake_db.tables[index.LETTERS_TABLE_NAME].keys())
        self.assertNotIn("stale-sync-id", remaining_ids)
        self.assertIn("manual-id", remaining_ids)
        self.assertIn("guest:john_smith", remaining_ids)

    def test_sync_returns_500_on_dynamo_error(self):
        mock_dynamo = MagicMock()
        mock_dynamo.get_all.side_effect = Exception("dynamo exploded")

        event = self.make_event("/miatun/sync", method="POST", headers=self.auth_headers)
        with patch.object(index, "CW_DYNAMO_CLIENT", mock_dynamo):
            response = index.handler(event, self.make_context())

        self.assertEqual(response["statusCode"], 500)

    def test_list_letters(self):
        self.fake_db.tables[index.LETTERS_TABLE_NAME] = {
            "l1": make_raw_letter("l1", guest="John Smith", gifts=[{"gift": "Stand Mixer", "brand": "", "price_cents": None}])
        }

        event = self.make_event("/miatun/letter", headers=self.auth_headers)
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(len(body["letters"]), 1)
        self.assertEqual(body["letters"][0]["guest"], "John Smith")
        self.assertEqual(body["letters"][0]["gifts"][0]["gift"], "Stand Mixer")

    def test_list_letters_rejects_missing_api_key(self):
        event = self.make_event("/miatun/letter")
        response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 401)

    def test_create_letter_manual(self):
        payload = {
            "guest": "Amy Pond",
            "gifts": [{"gift": "Hand-knit Scarf", "brand": "", "price_cents": None}],
            "letter_body": "",
        }
        event = self.make_event(
            "/miatun/letter", method="POST", headers=self.auth_headers, body=payload
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["letter"]["guest"], "Amy Pond")
        self.assertEqual(body["letter"]["gifts"][0]["gift"], "Hand-knit Scarf")
        self.assertEqual(body["letter"]["status"], "DRAFT")
        self.assertEqual(body["letter"]["source"], "MANUAL")
        self.assertEqual(len(self.fake_db.tables[index.LETTERS_TABLE_NAME]), 1)

    def test_patch_letter_updates_body_and_status(self):
        letter_id = "l1"
        self.fake_db.tables[index.LETTERS_TABLE_NAME] = {
            letter_id: make_raw_letter(letter_id, guest="John Smith", gifts=[{"gift": "Stand Mixer", "brand": "", "price_cents": None}])
        }
        payload = {
            "letter_id": letter_id,
            "letter_body": "Dear John, thank you!",
            "status": "WRITTEN",
        }
        event = self.make_event(
            "/miatun/letter", method="PATCH", headers=self.auth_headers, body=payload
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["letter"]["letter_body"], "Dear John, thank you!")
        self.assertEqual(body["letter"]["status"], "WRITTEN")
        self.assertEqual(body["letter"]["guest"], "John Smith")
        # gifts untouched by a body/status-only edit
        self.assertEqual(body["letter"]["gifts"][0]["gift"], "Stand Mixer")

    def test_patch_missing_letter_id(self):
        event = self.make_event(
            "/miatun/letter", method="PATCH", headers=self.auth_headers, body={}
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 400)

    def test_patch_not_found(self):
        event = self.make_event(
            "/miatun/letter",
            method="PATCH",
            headers=self.auth_headers,
            body={"letter_id": "nope", "letter_body": "x"},
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 404)

    def test_delete_letter_then_list_is_empty(self):
        letter_id = "l1"
        self.fake_db.tables[index.LETTERS_TABLE_NAME] = {
            letter_id: make_raw_letter(letter_id, guest="John Smith", gifts=[{"gift": "Stand Mixer", "brand": "", "price_cents": None}])
        }

        delete_event = self.make_event(
            "/miatun/letter",
            method="DELETE",
            headers=self.auth_headers,
            body={"letter_id": letter_id},
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            delete_response = index.handler(delete_event, self.make_context())
        self.assertEqual(delete_response["statusCode"], 200)

        list_event = self.make_event("/miatun/letter", headers=self.auth_headers)
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            list_response = index.handler(list_event, self.make_context())
        list_body = json.loads(list_response["body"])
        self.assertEqual(list_body["letters"], [])

    def test_delete_missing_letter_id(self):
        event = self.make_event(
            "/miatun/letter", method="DELETE", headers=self.auth_headers, body={}
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 400)

    def test_delete_not_found(self):
        event = self.make_event(
            "/miatun/letter",
            method="DELETE",
            headers=self.auth_headers,
            body={"letter_id": "nope"},
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 404)

    def test_unknown_route_404(self):
        event = self.make_event(
            "/miatun/nope", headers={"x-first-last": "john_smith"}
        )
        response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 404)


class TestDisjoinLetterPair(unittest.TestCase):
    """Test suite for POST /miatun/disjoin through the full handler."""

    @staticmethod
    def make_event(path, method="GET", headers=None, body=None):
        event = {
            "version": "2.0",
            "rawPath": path,
            "rawQueryString": "",
            "headers": headers or {},
            "requestContext": {
                "http": {"method": method, "path": path, "sourceIp": "127.0.0.1"},
                "requestId": "test-request-id",
                "stage": "$default",
            },
            "isBase64Encoded": False,
        }
        if body is not None:
            event["body"] = json.dumps(body)
        return event

    @staticmethod
    def make_context():
        ctx = MagicMock()
        ctx.function_name = "miatun"
        ctx.memory_limit_in_mb = 512
        ctx.invoked_function_arn = (
            "arn:aws:lambda:us-east-1:123456789012:function:miatun"
        )
        ctx.aws_request_id = "test-aws-request-id"
        return ctx

    def setUp(self):
        self.fake_db = FakeDynamoDB()
        self.auth_headers = {"Internal-Api-Key": "test_internal_key"}

    def seed_couple(self, both_claim_a_gift=True):
        """John and Jane are paired (guest_pair_first_last); Jane always
        claims a gift, John optionally claims a separate one too."""
        items = {
            "i1": make_raw_item("i1", "Toaster", claimant_id="jane_smith"),
        }
        claims = {
            "c1": make_raw_claim("c1", "i1", "jane_smith"),
        }
        if both_claim_a_gift:
            items["i2"] = make_raw_item("i2", "Blender", claimant_id="john_smith")
            claims["c2"] = make_raw_claim("c2", "i2", "john_smith")

        self.fake_db.tables[index.REGISTRY_ITEM_TABLE_NAME] = items
        self.fake_db.tables[index.REGISTRY_CLAIM_TABLE_NAME] = claims
        self.fake_db.tables[index.USER_TABLE_NAME] = {
            "jane_smith": make_raw_user("jane_smith", pair="john_smith"),
            "john_smith": make_raw_user("john_smith", pair="jane_smith"),
        }

    def run_sync(self):
        event = self.make_event("/miatun/sync", method="POST", headers=self.auth_headers)
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 200)

    def disjoin(self, letter_id):
        event = self.make_event(
            "/miatun/disjoin",
            method="POST",
            headers=self.auth_headers,
            body={"letter_id": letter_id},
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            return index.handler(event, self.make_context())

    def test_disjoin_rejects_missing_api_key(self):
        event = self.make_event(
            "/miatun/disjoin", method="POST", body={"letter_id": "x"}
        )
        response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 401)

    def test_disjoin_rejects_wrong_api_key(self):
        event = self.make_event(
            "/miatun/disjoin",
            method="POST",
            headers={"internal-api-key": "wrong"},
            body={"letter_id": "x"},
        )
        response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 401)

    def test_disjoin_missing_letter_id(self):
        event = self.make_event(
            "/miatun/disjoin", method="POST", headers=self.auth_headers, body={}
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 400)

    def test_disjoin_letter_not_found(self):
        response = self.disjoin("nope")
        self.assertEqual(response["statusCode"], 404)

    def test_disjoin_rejects_manual_letter(self):
        self.fake_db.tables[index.LETTERS_TABLE_NAME] = {
            "manual-1": make_raw_letter(
                "manual-1", source="MANUAL", guest="Jane Smith", partner="John Smith"
            ),
        }
        response = self.disjoin("manual-1")
        self.assertEqual(response["statusCode"], 400)

    def test_disjoin_rejects_letter_with_no_claimant(self):
        self.fake_db.tables[index.LETTERS_TABLE_NAME] = {
            "item:i1": make_raw_letter(
                "item:i1", source="SYNC", guest="", claimant_id=""
            ),
        }
        response = self.disjoin("item:i1")
        self.assertEqual(response["statusCode"], 400)

    def test_disjoin_rejects_when_no_partner_on_file(self):
        self.fake_db.tables[index.LETTERS_TABLE_NAME] = {
            "guest:amy_pond": make_raw_letter(
                "guest:amy_pond", source="SYNC", guest="Amy Pond", claimant_id="amy_pond"
            ),
        }
        self.fake_db.tables[index.USER_TABLE_NAME] = {
            "amy_pond": make_raw_user("amy_pond", pair=""),
        }
        response = self.disjoin("guest:amy_pond")
        self.assertEqual(response["statusCode"], 400)

    def test_disjoin_happy_path_splits_couple_with_correct_gift_attribution(self):
        self.seed_couple(both_claim_a_gift=True)
        self.run_sync()

        response = self.disjoin("couple:jane_smith|john_smith")
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(len(body["letters"]), 2)

        by_id = {letter.id: letter for letter in index.LetterRecord.get_all_letters_db(self.fake_db)}
        self.assertIn("guest:jane_smith", by_id)
        self.assertIn("guest:john_smith", by_id)
        self.assertNotIn("couple:jane_smith|john_smith", by_id)
        self.assertEqual(by_id["guest:jane_smith"].partner, "")
        self.assertEqual(by_id["guest:john_smith"].partner, "")
        self.assertEqual([g["gift"] for g in by_id["guest:jane_smith"].gifts], ["Toaster"])
        self.assertEqual([g["gift"] for g in by_id["guest:john_smith"].gifts], ["Blender"])

    def test_disjoin_is_durable_across_subsequent_sync(self):
        self.seed_couple(both_claim_a_gift=True)
        self.run_sync()
        self.disjoin("couple:jane_smith|john_smith")

        pair_table = self.fake_db.tables[index.LETTERS_DISJOINED_PAIRS_TABLE_NAME]
        self.assertIn("jane_smith|john_smith", pair_table)

        self.run_sync()

        remaining_ids = set(self.fake_db.tables[index.LETTERS_TABLE_NAME].keys())
        self.assertIn("guest:jane_smith", remaining_ids)
        self.assertIn("guest:john_smith", remaining_ids)
        self.assertNotIn("couple:jane_smith|john_smith", remaining_ids)

    def test_disjoin_preserves_letter_body_and_status_for_original_claimant(self):
        self.seed_couple(both_claim_a_gift=True)
        self.run_sync()

        letter = index.LetterRecord.from_letter_id_db(
            "couple:jane_smith|john_smith", self.fake_db
        )
        self.assertEqual(letter.claimant_id, "jane_smith")  # sorts first alphabetically
        letter.letter_body = "Dear Jane and John, thank you!"
        letter.status = index.LetterStatus.WRITTEN
        letter.update_db(self.fake_db)

        self.disjoin("couple:jane_smith|john_smith")

        by_id = {letter.id: letter for letter in index.LetterRecord.get_all_letters_db(self.fake_db)}
        self.assertEqual(by_id["guest:jane_smith"].letter_body, "Dear Jane and John, thank you!")
        self.assertEqual(by_id["guest:jane_smith"].status, index.LetterStatus.WRITTEN)
        self.assertEqual(by_id["guest:john_smith"].letter_body, "")
        self.assertEqual(by_id["guest:john_smith"].status, index.LetterStatus.DRAFT)

    def test_disjoin_partner_with_no_claimed_gifts_yields_single_letter(self):
        self.seed_couple(both_claim_a_gift=False)
        self.run_sync()

        response = self.disjoin("couple:jane_smith|john_smith")
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(len(body["letters"]), 1)
        self.assertEqual(body["letters"][0]["id"], "guest:jane_smith")

        remaining_ids = set(self.fake_db.tables[index.LETTERS_TABLE_NAME].keys())
        self.assertNotIn("guest:john_smith", remaining_ids)

    def test_redisjoin_after_prune_returns_404(self):
        self.seed_couple(both_claim_a_gift=True)
        self.run_sync()
        first = self.disjoin("couple:jane_smith|john_smith")
        self.assertEqual(first["statusCode"], 200)

        second = self.disjoin("couple:jane_smith|john_smith")
        self.assertEqual(second["statusCode"], 404)

    def test_disjoin_returns_500_on_dynamo_error(self):
        # from_letter_id_db/get_user_db swallow their own errors (return
        # None/{}, surfacing as 404s elsewhere), so to exercise the 500 path
        # a real letter+partner must resolve first — only the recompute
        # step's get_all() call blows up.
        self.seed_couple(both_claim_a_gift=True)
        self.run_sync()

        mock_dynamo = MagicMock(wraps=self.fake_db)
        mock_dynamo.get_all.side_effect = Exception("dynamo exploded")

        event = self.make_event(
            "/miatun/disjoin",
            method="POST",
            headers=self.auth_headers,
            body={"letter_id": "couple:jane_smith|john_smith"},
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", mock_dynamo):
            response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 500)


class TestLetterStatusAndLimits(unittest.TestCase):
    """READY_TO_SEND status and the LETTER_BODY_MAX_CHARS cap."""

    make_event = staticmethod(TestAPIEndpoints.make_event)
    make_context = staticmethod(TestAPIEndpoints.make_context)

    def setUp(self):
        self.fake_db = FakeDynamoDB()
        self.auth_headers = {"Internal-Api-Key": "test_internal_key"}
        self.fake_db.tables[index.LETTERS_TABLE_NAME] = {
            "l1": make_raw_letter("l1", guest="John Smith")
        }

    def patch_letter(self, payload):
        event = self.make_event(
            "/miatun/letter", method="PATCH", headers=self.auth_headers,
            body={"letter_id": "l1", **payload},
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            return index.handler(event, self.make_context())

    def test_ready_to_send_round_trips(self):
        response = self.patch_letter({"status": "READY_TO_SEND"})
        self.assertEqual(response["statusCode"], 200)
        letter = index.LetterRecord.from_letter_id_db("l1", self.fake_db)
        self.assertEqual(letter.status, index.LetterStatus.READY_TO_SEND)
        self.assertEqual(letter.as_map()["status"], "READY_TO_SEND")

    def test_patch_accepts_500_char_body(self):
        response = self.patch_letter({"letter_body": "x" * 500})
        self.assertEqual(response["statusCode"], 200)

    def test_patch_rejects_501_char_body(self):
        response = self.patch_letter({"letter_body": "x" * 501})
        self.assertEqual(response["statusCode"], 400)
        letter = index.LetterRecord.from_letter_id_db("l1", self.fake_db)
        self.assertEqual(letter.letter_body, "")

    def test_create_rejects_501_char_body(self):
        event = self.make_event(
            "/miatun/letter", method="POST", headers=self.auth_headers,
            body={"guest": "Amy Pond", "letter_body": "x" * 501},
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(len(self.fake_db.tables[index.LETTERS_TABLE_NAME]), 1)

    def test_create_accepts_500_char_body(self):
        event = self.make_event(
            "/miatun/letter", method="POST", headers=self.auth_headers,
            body={"guest": "Amy Pond", "letter_body": "x" * 500},
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db):
            response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 200)


class TestEnvelopeName(unittest.TestCase):
    def test_solo(self):
        self.assertEqual(index.envelope_name("Jane Doe", ""), ("Jane", "Doe"))

    def test_solo_single_token(self):
        self.assertEqual(index.envelope_name("Cher", ""), ("Cher", ""))

    def test_couple_shared_last_name(self):
        self.assertEqual(
            index.envelope_name("Jane Smith", "John Smith"), ("Jane & John", "Smith")
        )

    def test_couple_different_last_names(self):
        self.assertEqual(
            index.envelope_name("Jane Doe", "John Smith"), ("Jane Doe &", "John Smith")
        )


HANDWRYTTEN_TEST_CONFIG = {
    "HANDWRYTTEN_API_KEY": "hw_test_key",
    "HANDWRYTTEN_CARD_ID": "123",
    "HANDWRYTTEN_FONT_LABEL": "hwJenna",
    "HANDWRYTTEN_WISHES": "With love, Mitzi & Matthew",
    "HANDWRYTTEN_SENDER": json.dumps(
        {
            "first_name": "Mitzi",
            "last_name": "Saucedo",
            "address1": "1 Home St",
            "city": "Austin",
            "state": "TX",
            "zip": "78701",
        }
    ),
}


def make_ready_letter(letter_id, guest, status="READY_TO_SEND", **fields):
    defaults = {
        "guest": guest,
        "street": "123 Main St",
        "city": "Brooklyn",
        "state_loc": "NY",
        "zipcode": "11201",
        "country": "USA",
        "letter_body": f"Dear {guest}, thank you!",
        "status": status,
    }
    defaults.update(fields)
    return make_raw_letter(letter_id, **defaults)


class TestSendLetters(unittest.TestCase):
    """POST /miatun/send and /miatun/send-one, with Handwrytten mocked."""

    make_event = staticmethod(TestAPIEndpoints.make_event)
    make_context = staticmethod(TestAPIEndpoints.make_context)

    def setUp(self):
        self.fake_db = FakeDynamoDB()
        self.auth_headers = {"Internal-Api-Key": "test_internal_key"}
        self.fake_db.tables[index.LETTERS_TABLE_NAME] = {
            "l1": make_ready_letter("l1", "Jane Doe", partner="John Doe"),
            "l2": make_ready_letter("l2", "Amy Pond"),
            "l3": make_ready_letter("l3", "Rory Williams", status="WRITTEN"),
        }
        self.hw = MagicMock()
        self.hw.get_card.return_value = {"id": 123, "characters": 400}
        self.hw.basket_count.return_value = 0
        self.hw.place_basket.return_value = {"order_id": 777}
        self.hw.send_basket.return_value = {"status": "ok"}

    def call(self, path, body):
        event = self.make_event(path, method="POST", headers=self.auth_headers, body=body)
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db), patch.object(
            index, "get_handwrytten_client", return_value=self.hw
        ), patch.multiple(index, **HANDWRYTTEN_TEST_CONFIG):
            response = index.handler(event, self.make_context())
        return response["statusCode"], json.loads(response["body"])

    def status_of(self, letter_id):
        return index.LetterRecord.from_letter_id_db(letter_id, self.fake_db).status

    def assert_no_basket_calls(self):
        self.hw.basket_count.assert_not_called()
        self.hw.place_basket.assert_not_called()
        self.hw.send_basket.assert_not_called()

    def test_send_rejects_missing_api_key(self):
        event = self.make_event("/miatun/send", method="POST", body={})
        response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 401)

    def test_send_defaults_to_dry_run(self):
        status, body = self.call("/miatun/send", {})
        self.assertEqual(status, 200)
        self.assertTrue(body["dry_run"])
        self.assertEqual(body["count"], 2)
        self.assertEqual(body["max_chars"], 400)
        self.assert_no_basket_calls()
        self.assertEqual(self.status_of("l1"), index.LetterStatus.READY_TO_SEND)

    def test_dry_run_previews_recipients(self):
        status, body = self.call("/miatun/send", {"dry_run": True})
        self.assertEqual(status, 200)
        by_id = {r["letter_id"]: r for r in body["recipients"]}
        self.assertEqual(set(by_id), {"l1", "l2"})  # WRITTEN l3 excluded
        couple = by_id["l1"]
        self.assertEqual(couple["to_first_name"], "Jane & John")
        self.assertEqual(couple["to_last_name"], "Doe")
        self.assertEqual(couple["to_zip"], "11201")
        self.assertEqual(couple["message"], "Dear Jane Doe, thank you!")
        self.assertEqual(couple["wishes"], "With love, Mitzi & Matthew")
        self.assertEqual(couple["from_city"], "Austin")
        self.assertNotIn("to_address2", couple)

    def test_send_success_submits_basket_once_and_marks_sent(self):
        status, body = self.call("/miatun/send", {"dry_run": False})
        self.assertEqual(status, 200)
        self.assertEqual(body["count"], 2)
        self.assertEqual(body["handwrytten_order_id"], "777")
        self.hw.place_basket.assert_called_once()
        self.hw.send_basket.assert_called_once()
        card_id, font, rows = self.hw.place_basket.call_args.args
        self.assertEqual((card_id, font, len(rows)), ("123", "hwJenna", 2))

        for letter_id in ("l1", "l2"):
            letter = index.LetterRecord.from_letter_id_db(letter_id, self.fake_db)
            self.assertEqual(letter.status, index.LetterStatus.SENT)
            self.assertEqual(letter.handwrytten_order_id, "777")
            self.assertTrue(letter.sent_at)
        self.assertEqual(self.status_of("l3"), index.LetterStatus.WRITTEN)

    def test_send_mark_sent_false_leaves_statuses(self):
        status, _ = self.call("/miatun/send", {"dry_run": False, "mark_sent": False})
        self.assertEqual(status, 200)
        self.hw.send_basket.assert_called_once()
        self.assertEqual(self.status_of("l1"), index.LetterStatus.READY_TO_SEND)

    def test_one_invalid_letter_blocks_whole_batch(self):
        self.fake_db.tables[index.LETTERS_TABLE_NAME]["l2"] = make_ready_letter(
            "l2", "Amy Pond", zipcode=""
        )
        status, body = self.call("/miatun/send", {"dry_run": False})
        self.assertEqual(status, 400)
        self.assertEqual(body["invalid_letters"][0]["letter_id"], "l2")
        self.assertIn("missing zip", body["invalid_letters"][0]["problems"])
        self.assert_no_basket_calls()
        self.assertEqual(self.status_of("l1"), index.LetterStatus.READY_TO_SEND)

    def test_body_longer_than_card_capacity_is_invalid(self):
        self.hw.get_card.return_value = {"id": 123, "characters": 20}
        status, body = self.call("/miatun/send", {"dry_run": False})
        self.assertEqual(status, 400)
        self.assertEqual(body["max_chars"], 20)
        self.assert_no_basket_calls()

    def test_non_us_country_is_invalid(self):
        self.fake_db.tables[index.LETTERS_TABLE_NAME]["l2"] = make_ready_letter(
            "l2", "Amy Pond", country="Canada"
        )
        status, body = self.call("/miatun/send", {"dry_run": True})
        self.assertEqual(status, 400)
        self.assertIn("non-US", body["invalid_letters"][0]["problems"][0])

    def test_empty_body_is_invalid(self):
        self.fake_db.tables[index.LETTERS_TABLE_NAME]["l2"] = make_ready_letter(
            "l2", "Amy Pond", letter_body="   "
        )
        status, body = self.call("/miatun/send", {"dry_run": True})
        self.assertEqual(status, 400)
        self.assertIn("letter body is empty", body["invalid_letters"][0]["problems"])

    def test_nonempty_basket_aborts(self):
        self.hw.basket_count.return_value = 3
        status, _ = self.call("/miatun/send", {"dry_run": False})
        self.assertEqual(status, 409)
        self.hw.place_basket.assert_not_called()
        self.hw.send_basket.assert_not_called()
        self.assertEqual(self.status_of("l1"), index.LetterStatus.READY_TO_SEND)

    def test_checkout_failure_does_not_mark_sent(self):
        self.hw.send_basket.side_effect = index.HandwryttenError("card declined")
        status, body = self.call("/miatun/send", {"dry_run": False})
        self.assertEqual(status, 502)
        self.assertIn("card declined", body["error"])
        self.assertEqual(self.status_of("l1"), index.LetterStatus.READY_TO_SEND)

    def test_card_lookup_failure_returns_502(self):
        self.hw.get_card.side_effect = index.HandwryttenError("bad api key")
        status, _ = self.call("/miatun/send", {"dry_run": True})
        self.assertEqual(status, 502)

    def test_no_ready_letters(self):
        self.fake_db.tables[index.LETTERS_TABLE_NAME] = {
            "l3": make_ready_letter("l3", "Rory Williams", status="WRITTEN")
        }
        status, _ = self.call("/miatun/send", {"dry_run": True})
        self.assertEqual(status, 400)

    def test_missing_config_returns_500(self):
        event = self.make_event(
            "/miatun/send", method="POST", headers=self.auth_headers, body={"dry_run": True}
        )
        with patch.object(index, "CW_DYNAMO_CLIENT", self.fake_db), patch.object(
            index, "get_handwrytten_client", return_value=self.hw
        ), patch.multiple(index, **{**HANDWRYTTEN_TEST_CONFIG, "HANDWRYTTEN_API_KEY": ""}):
            response = index.handler(event, self.make_context())
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("handwrytten_api_key", json.loads(response["body"])["message"])

    def test_send_one_sends_only_that_letter(self):
        status, body = self.call("/miatun/send-one", {"letter_id": "l3", "dry_run": False})
        self.assertEqual(status, 200)
        self.assertEqual(body["letter_ids"], ["l3"])
        _, _, rows = self.hw.place_basket.call_args.args
        self.assertEqual(len(rows), 1)
        self.assertEqual(self.status_of("l3"), index.LetterStatus.SENT)
        # READY_TO_SEND letters are not swept in
        self.assertEqual(self.status_of("l1"), index.LetterStatus.READY_TO_SEND)

    def test_send_one_dry_run(self):
        status, body = self.call("/miatun/send-one", {"letter_id": "l3"})
        self.assertEqual(status, 200)
        self.assertTrue(body["dry_run"])
        self.assert_no_basket_calls()

    def test_send_one_refuses_already_sent(self):
        self.fake_db.tables[index.LETTERS_TABLE_NAME]["l4"] = make_ready_letter(
            "l4", "Clara Oswald", status="SENT"
        )
        status, _ = self.call("/miatun/send-one", {"letter_id": "l4", "dry_run": False})
        self.assertEqual(status, 409)
        self.assert_no_basket_calls()

    def test_send_one_unknown_letter(self):
        status, _ = self.call("/miatun/send-one", {"letter_id": "nope"})
        self.assertEqual(status, 404)

    def test_send_one_requires_letter_id(self):
        status, _ = self.call("/miatun/send-one", {})
        self.assertEqual(status, 400)


class TestHandwryttenClient(unittest.TestCase):
    """Request shape of the urllib-based Handwrytten client."""

    @staticmethod
    def fake_response(payload):
        res = MagicMock()
        res.read.return_value = json.dumps(payload).encode()
        res.__enter__.return_value = res
        return res

    def test_place_basket_request(self):
        client = index.HandwryttenClient("hw_key")
        with patch.object(
            index.urllib.request, "urlopen", return_value=self.fake_response({"order_id": 5})
        ) as urlopen:
            result = client.place_basket("123", "hwJenna", [{"to_first_name": "Jane"}])
        self.assertEqual(result, {"order_id": 5})
        req = urlopen.call_args.args[0]
        self.assertEqual(req.full_url, "https://api.handwrytten.com/v2/orders/placeBasket")
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.get_header("Authorization"), "hw_key")
        self.assertEqual(
            json.loads(req.data),
            {"card_id": 123, "font": "hwJenna", "addresses": [{"to_first_name": "Jane"}]},
        )

    def test_get_card_query_string(self):
        client = index.HandwryttenClient("hw_key")
        with patch.object(
            index.urllib.request, "urlopen",
            return_value=self.fake_response({"card": {"id": 123, "characters": 340}}),
        ) as urlopen:
            card = client.get_card("123")
        self.assertEqual(card["characters"], 340)
        self.assertEqual(
            urlopen.call_args.args[0].full_url,
            "https://api.handwrytten.com/v2/cards/view?card_id=123",
        )

    def test_status_error_body_raises(self):
        client = index.HandwryttenClient("hw_key")
        with patch.object(
            index.urllib.request, "urlopen",
            return_value=self.fake_response({"status": "error", "message": "nope"}),
        ):
            with self.assertRaises(index.HandwryttenError):
                client.basket_count()


if __name__ == "__main__":
    unittest.main()
