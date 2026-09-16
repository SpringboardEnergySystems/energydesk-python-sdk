from unittest import TestCase

from energydeskapi.types.multi_leg_deals import (
    AddLegWrite,
    ContractGroupTypeEnum,
    CreatePackageWrite,
    DealPackage,
    FeeAllocationEnum,
    GroupFeeTypeEnum,
    Leg,
    LegRoleEnum,
    PackageVersion,
    PublishPackageOfferWrite,
    contract_group_type_description,
    fee_allocation_description,
    group_fee_type_description,
    leg_role_description,
)

# Wire-value snapshots of the appserver's frozen codes (portfoliomanager
# *_CHOICES tuples, appserver PR #415 "DealPackage origination completion")
# - a rename/removal on that side breaks this test instead of silently
# drifting. Keep in sync with energydesk/apps/portfoliomanager/models.py.
DJANGO_LEG_ROLE_VALUES = {
    "FIXED_PRICE", "FLOATING_PRICE", "VOLUME_BLOCK", "CERTIFICATE",
    "FINANCIAL_HEDGE", "FEE", "HEDGE",
}
DJANGO_CONTRACT_GROUP_TYPE_VALUES = {
    "ORIGINATED_PACKAGE", "HEDGED_STRUCTURE", "SYNTHETIC", "MANUAL",
}
DJANGO_GROUP_FEE_TYPE_VALUES = {
    "STRUCTURING", "ORIGINATION", "MANAGEMENT", "BALANCING_SERVICE",
}
DJANGO_FEE_ALLOCATION_VALUES = {
    "GROUP_LEVEL", "PRO_RATA_NOTIONAL", "PRO_RATA_VOLUME", "PRIMARY_CONTRACT",
}


class TestEnumsMirrorDjangoChoices(TestCase):
    def test_leg_role_enum_matches_django(self):
        self.assertEqual({e.value for e in LegRoleEnum}, DJANGO_LEG_ROLE_VALUES)

    def test_contract_group_type_enum_matches_django(self):
        self.assertEqual({e.value for e in ContractGroupTypeEnum}, DJANGO_CONTRACT_GROUP_TYPE_VALUES)

    def test_group_fee_type_enum_matches_django(self):
        self.assertEqual({e.value for e in GroupFeeTypeEnum}, DJANGO_GROUP_FEE_TYPE_VALUES)

    def test_fee_allocation_enum_matches_django(self):
        self.assertEqual({e.value for e in FeeAllocationEnum}, DJANGO_FEE_ALLOCATION_VALUES)

    def test_every_enum_value_has_a_description(self):
        for e in LegRoleEnum:
            self.assertIsInstance(leg_role_description(e), str)
        for e in ContractGroupTypeEnum:
            self.assertIsInstance(contract_group_type_description(e), str)
        for e in GroupFeeTypeEnum:
            self.assertIsInstance(group_fee_type_description(e), str)
        for e in FeeAllocationEnum:
            self.assertIsInstance(fee_allocation_description(e), str)


class TestLeg(TestCase):
    def test_parses_an_add_leg_response(self):
        raw = {
            "pk": 501,
            "reference": "DEAL-000501",
            "title": "Leg 1 - fixed price",
            "status": {"code": "DRAFT", "description": "Draft"},
            "template": {"pk": 7, "title": "PPA Template"},
            "counterpart": None,
            "buy_or_sell": "BUY",
            "trading_book": 3,
            "price_area": "NO1",
            "delivery_from": "2028-01-01T00:00:00Z",
            "delivery_until": "2029-01-01T00:00:00Z",
            "current_version": None,
            "contract": None,
            "originator": 12,
            "created_at": "2026-09-16T09:00:00Z",
            "updated_at": "2026-09-16T09:00:00Z",
        }
        leg = Leg(**raw)
        self.assertEqual(leg.reference, "DEAL-000501")
        self.assertEqual(leg.buy_or_sell, "BUY")
        # leg_no/leg_role/account/package are not on the wire yet (appserver
        # gap - DealEmbeddedSerializer wasn't updated for the new Deal FKs).
        self.assertFalse(hasattr(leg, "leg_no"))


class TestPackageVersion(TestCase):
    def test_parses_a_realistic_payload(self):
        raw = {
            "pk": 91,
            "package": "http://testserver/api/origination/packages/12/",
            "version_no": 1,
            "label": "Initial",
            "leg_versions": {"501": 1},
            "package_fees": {"STRUCTURING": 1500.0},
            "price_summary": {"total": 148000.0, "currency": "EUR"},
            "is_locked": False,
            "comment": "",
            "created_by": 12,
            "created_at": "2026-09-16T09:05:00Z",
        }
        version = PackageVersion(**raw)
        self.assertEqual(version.version_no, 1)
        self.assertEqual(version.package_fees, {"STRUCTURING": 1500.0})


class TestDealPackage(TestCase):
    def test_parses_a_realistic_payload(self):
        raw = {
            "pk": 12,
            "reference": "PKG-000012",
            "title": "Statkraft PPA package",
            "status": {"code": "DRAFT", "description": "Draft"},
            "contract_owner": 1,
            "counterpart": {"pk": 44, "name": "Statkraft"},
            "trading_book": 3,
            "account": None,
            "current_version": "http://testserver/api/origination/package-versions/91/",
            "contract_group": None,
            "originator": 12,
            "updated_by": 12,
            "source": "MANUAL",
            "notes": "",
            "created_at": "2026-09-16T09:00:00Z",
            "updated_at": "2026-09-16T09:05:00Z",
        }
        package = DealPackage(**raw)
        self.assertEqual(package.reference, "PKG-000012")
        self.assertEqual(package.counterpart["name"], "Statkraft")


class TestCreatePackageWrite(TestCase):
    def test_only_trading_book_required(self):
        write = CreatePackageWrite(trading_book=3)
        self.assertEqual(write.title, "")
        self.assertIsNone(write.counterpart)

    def test_round_trips_a_full_payload(self):
        raw = {
            "title": "Statkraft PPA package",
            "contract_owner": 1,
            "counterpart": 44,
            "trading_book": 3,
            "account": 9,
            "source": "MANUAL",
            "notes": "Origination desk draft",
        }
        write = CreatePackageWrite(**raw)
        self.assertEqual(write.model_dump(), raw)


class TestAddLegWrite(TestCase):
    def test_round_trips_a_full_payload(self):
        raw = {
            "template": 7,
            "delivery_from": "2028-01-01T00:00:00Z",
            "delivery_until": "2029-01-01T00:00:00Z",
            "leg_role": 2,
            "title": "Leg 1",
            "commodity": 5,
            "price_area": "NO1",
            "asset": None,
            "portfolio": None,
            "buy_or_sell": "BUY",
        }
        write = AddLegWrite(**raw)
        self.assertEqual(write.template, 7)
        self.assertEqual(write.buy_or_sell, "BUY")

    def test_optional_fields_default(self):
        write = AddLegWrite(
            template=7,
            delivery_from="2028-01-01T00:00:00Z",
            delivery_until="2029-01-01T00:00:00Z",
        )
        self.assertEqual(write.title, "")
        self.assertIsNone(write.leg_role)


class TestPublishPackageOfferWrite(TestCase):
    def test_has_no_kind_field(self):
        # The wrapper injects `kind` internally (see pydantic_types module
        # docstring) - it must never be part of the SDK's public write shape.
        self.assertNotIn("kind", PublishPackageOfferWrite.model_fields)

    def test_round_trips_a_full_payload(self):
        raw = {
            "offered_to": 44,
            "valid_until": "2026-10-01T00:00:00Z",
            "price_amount": "48.20",
            "price_currency": "EUR",
        }
        write = PublishPackageOfferWrite(**raw)
        self.assertEqual(str(write.price_amount), "48.20")
        self.assertEqual(write.price_currency, "EUR")

    def test_defaults_when_only_valid_until_given(self):
        write = PublishPackageOfferWrite(valid_until="2026-10-01T00:00:00Z")
        self.assertIsNone(write.offered_to)
        self.assertEqual(write.price_currency, "EUR")
