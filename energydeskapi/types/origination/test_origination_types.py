from unittest import TestCase

from pydantic import ValidationError

from energydeskapi.types.origination import (
    ContractFamilyEnum,
    DealStatusEnum,
    OfferKindEnum,
    OfferStatusEnum,
    OPEN_OFFER_STATUSES,
    Pricing,
    Profile,
    ProfilePeriod,
    Terms,
    contract_family_description,
    deal_status_description,
    offer_kind_description,
    offer_status_description,
)
from energydeskapi.types.origination.terms import RuleObject


# Wire-value snapshots of the Django-side choices this module mirrors, so a
# rename/removal on the appserver side breaks this test instead of silently
# drifting. Keep these lists in sync with:
#   energydesk/apps/portfoliomanager/models.py::CONTRACT_FAMILY_CHOICES
#   energydesk/apps/origination/models.py::DEAL_STATUS_CHOICES / OFFER_KIND_CHOICES / OFFER_STATUS_CHOICES
DJANGO_CONTRACT_FAMILY_VALUES = {
    "STANDARD", "FINANCIAL_BILATERAL", "PHYSICAL_STRUCTURED",
    "CERTIFICATE", "CAPACITY", "FX", "TRANSFER",
}
DJANGO_DEAL_STATUS_VALUES = {
    "DRAFT", "IN_APPROVAL", "APPROVED", "PUBLISHED", "NEGOTIATING",
    "ACCEPTED", "CONTRACTED", "DECLINED", "EXPIRED", "CANCELLED",
}
DJANGO_OFFER_KIND_VALUES = {"INDICATIVE", "FIRM"}
DJANGO_OFFER_STATUS_VALUES = {
    "PUBLISHED", "VIEWED", "ACCEPTED", "DECLINED", "COUNTERED", "EXPIRED", "WITHDRAWN",
}


class TestEnumsMirrorDjangoChoices(TestCase):
    def test_contract_family_enum_matches_django(self):
        self.assertEqual({e.value for e in ContractFamilyEnum}, DJANGO_CONTRACT_FAMILY_VALUES)

    def test_deal_status_enum_matches_django(self):
        self.assertEqual({e.value for e in DealStatusEnum}, DJANGO_DEAL_STATUS_VALUES)

    def test_offer_kind_enum_matches_django(self):
        self.assertEqual({e.value for e in OfferKindEnum}, DJANGO_OFFER_KIND_VALUES)

    def test_offer_status_enum_matches_django(self):
        self.assertEqual({e.value for e in OfferStatusEnum}, DJANGO_OFFER_STATUS_VALUES)

    def test_open_offer_statuses_are_a_subset(self):
        self.assertTrue(set(OPEN_OFFER_STATUSES).issubset(set(OfferStatusEnum)))

    def test_every_enum_value_has_a_description(self):
        for e in ContractFamilyEnum:
            self.assertIsInstance(contract_family_description(e), str)
        for e in DealStatusEnum:
            self.assertIsInstance(deal_status_description(e), str)
        for e in OfferKindEnum:
            self.assertIsInstance(offer_kind_description(e), str)
        for e in OfferStatusEnum:
            self.assertIsInstance(offer_status_description(e), str)


class TestTerms(TestCase):
    def test_parses_a_full_ppa_terms_blob(self):
        raw = {
            "volume": {"type": "PAY_AS_PRODUCED", "forecast_basis": "P50"},
            "price": {"type": "FIXED", "amount": 48.20, "currency": "EUR"},
            "index": {"type": "NONE"},
            "shape": {"type": "AS_PRODUCED"},
            "imbalance": {"type": "SHARED", "producer_share": 0.5},
            "goo": {"type": "INCLUDED", "technology": "WIND", "country": "NO",
                    "vintage": "PRODUCTION_YEAR", "volume_pct": 100},
            "curtailment": {"type": "BUYER_TAKES_VOLUME_RISK"},
            "negative_price": {"type": "STOP_PRODUCTION", "threshold": -50, "currency": "EUR"},
            "settlement": {"type": "MONTHLY", "day_of_month": 15},
        }
        terms = Terms(**raw)
        self.assertEqual(terms.price.type, "FIXED")
        self.assertEqual(terms.price.amount, 48.20)  # extra param preserved
        self.assertIsNone(terms.credit)
        self.assertIsNone(terms.regulatory)

    def test_missing_type_is_rejected(self):
        with self.assertRaises(ValidationError):
            RuleObject(**{"amount": 48.20})

    def test_unknown_top_level_key_is_rejected(self):
        with self.assertRaises(ValidationError):
            Terms(**{"not_a_rule_key": {"type": "X"}})

    def test_a_template_specific_rule_type_round_trips_untouched(self):
        # A customer template can introduce a `price` type this SDK has never
        # heard of (e.g. a new FORMULA variant with bespoke params) - Terms
        # must not reject it, since rule_schema validation lives server-side.
        terms = Terms(price={"type": "SOME_FUTURE_TYPE", "custom_param": 1})
        self.assertEqual(terms.price.type, "SOME_FUTURE_TYPE")
        self.assertEqual(terms.price.model_dump()["custom_param"], 1)


class TestProfile(TestCase):
    def test_parses_profile_periods_by_alias(self):
        raw = [
            {"from": "2028-01-01T00:00:00Z", "until": "2029-01-01T00:00:00Z",
             "quantity_mwh": 146000, "price": 48.20},
        ]
        periods = [ProfilePeriod(**row) for row in raw]
        self.assertEqual(len(periods), 1)
        self.assertEqual(periods[0].quantity_mwh, 146000)

    def test_profile_type_alias_is_usable(self):
        periods: Profile = []
        self.assertEqual(periods, [])


class TestPricing(TestCase):
    def test_parses_the_readme_example_payload(self):
        raw = {
            "currency": "EUR",
            "priced_at": "2026-09-04T09:12:00Z",
            "pricer_version": "synth-1.4.2",
            "market_data_asof": "2026-09-04T10:14:00Z",
            "decomposition": {
                "forward_value": 52.10, "shape_adj": -0.80, "volume_risk_adj": -0.35,
                "imbalance_cost": -1.10, "goo_value": 1.30, "margin": -2.95,
                "fair_value": 50.95, "offer_price": 48.20,
            },
            "capture_price": 48.20,
            "goo_value_per_mwh": 1.25,
            "imbalance_cost_per_mwh": -0.72,
            "residual_merchant_pct": 14,
            "shape_risk": "LOW",
            "var_95": 1.12,
            "scenarios": {
                "P10": {"volume_mwh": 118000, "revenue": 5810000},
                "P50": {"volume_mwh": 146000, "revenue": 7040000},
                "P90": {"volume_mwh": 168000, "revenue": 8100000},
            },
            "merchant_baseline": {
                "expected_revenue": 7840000, "p10_revenue": 4920000, "p90_revenue": 10310000,
                "residual_merchant_pct": 100, "shape_risk": "HIGH",
            },
        }
        pricing = Pricing(**raw)
        self.assertEqual(pricing.decomposition.fair_value, 50.95)
        self.assertEqual(pricing.scenarios["P50"].revenue, 7040000)
        self.assertEqual(pricing.merchant_baseline.shape_risk, "HIGH")

    def test_unknown_top_level_field_is_preserved_not_rejected(self):
        raw = {
            "currency": "EUR",
            "priced_at": "2026-09-04T09:12:00Z",
            "pricer_version": "stub-0.1",
            "market_data_asof": "2026-09-04T09:12:00Z",
            "decomposition": {
                "forward_value": 1, "shape_adj": 0, "volume_risk_adj": 0,
                "imbalance_cost": 0, "goo_value": 0, "margin": 0,
                "fair_value": 1, "offer_price": 1,
            },
            "capture_price": 1,
            "scenarios": {},
            "merchant_baseline": {
                "expected_revenue": 1, "p10_revenue": 1, "p90_revenue": 1,
                "residual_merchant_pct": 100, "shape_risk": "HIGH",
            },
            "future_field_from_a_newer_pricer": {"anything": True},
        }
        pricing = Pricing(**raw)
        self.assertEqual(pricing.model_dump()["future_field_from_a_newer_pricer"], {"anything": True})
