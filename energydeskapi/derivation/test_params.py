from datetime import date
from unittest import TestCase

from pydantic import TypeAdapter, ValidationError

from energydeskapi.derivation.params import (
    DerivationRule,
    EuropeanOptionParams,
    OutsideWindowPolicy,
    RuleParams,
)


class TestEuropeanOptionParams(TestCase):
    def test_portion_pct_normalises_to_a_fraction(self):
        params = EuropeanOptionParams(
            strike=500.0, strike_currency="NOK", portion_pct=5.25,
            volatility=0.30, risk_free_rate=0.02,
            price_source={"area": "NO1", "currency": "NOK"},
        )
        self.assertAlmostEqual(params.portion, 0.0525)

    def test_portion_pct_already_a_fraction_is_left_alone(self):
        params = EuropeanOptionParams(
            strike=500.0, strike_currency="NOK", portion_pct=0.0525,
            volatility=0.30, risk_free_rate=0.02,
            price_source={"area": "NO1", "currency": "NOK"},
        )
        self.assertAlmostEqual(params.portion, 0.0525)

    def test_default_outside_window_is_zero(self):
        params = EuropeanOptionParams(
            strike=500.0, strike_currency="NOK", portion_pct=5.25,
            volatility=0.30, risk_free_rate=0.02,
            price_source={"area": "NO1", "currency": "NOK"},
        )
        self.assertEqual(params.outside_window, OutsideWindowPolicy.ZERO)


class TestDerivationRuleDiscriminatedUnion(TestCase):
    def test_production_b2c_rabatt_shape(self):
        """Plan 22 section 4.3's actual B2C Rabatt config."""
        rule = DerivationRule.model_validate({
            "name": "B2C Rabatt",
            "asset_group": "B2C",
            "valid_from": "2025-09-30",
            "valid_to": "2029-01-01",
            "config_valid_from": "2025-01-01",
            "config_valid_to": None,
            "params": {
                "rule_type": "EUROPEAN_OPTION",
                "strike": 500.0,
                "strike_currency": "NOK",
                "portion_pct": 5.25,
                "volatility": 0.30,
                "risk_free_rate": 0.02,
                "price_source": {"timeseries_type": "forward_curve", "area": "NO1", "currency": "NOK"},
                "outside_window": "zero",
            },
        })
        self.assertIsInstance(rule.params, EuropeanOptionParams)
        self.assertEqual(rule.valid_from, date(2025, 9, 30))
        self.assertAlmostEqual(rule.params.portion, 0.0525)

    def test_percentage_rule_shape(self):
        rule = DerivationRule.model_validate({
            "name": "Test flat reduction",
            "asset_group": "B2B",
            "params": {"rule_type": "PERCENTAGE", "factor_pct": -5.0},
        })
        self.assertEqual(rule.params.factor_pct, -5.0)

    def test_unknown_rule_type_rejected(self):
        with self.assertRaises(ValidationError):
            TypeAdapter(RuleParams).validate_python({"rule_type": "NOT_A_REAL_TYPE"})
