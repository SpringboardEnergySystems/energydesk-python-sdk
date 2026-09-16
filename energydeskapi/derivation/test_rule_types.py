from datetime import date
from unittest import TestCase

from energydeskapi.derivation.rule_types import (
    asian_option,
    european_option,
    fixed_offset,
    monthly_percentage,
    percentage,
)


class TestPercentage(TestCase):
    def test_reduction(self):
        self.assertAlmostEqual(percentage(-5.0).factor, 0.95)

    def test_uplift(self):
        self.assertAlmostEqual(percentage(5.0).factor, 1.05)

    def test_zero_is_pass_through(self):
        self.assertAlmostEqual(percentage(0.0).factor, 1.0)


class TestMonthlyPercentage(TestCase):
    def test_selects_the_delivery_periods_month(self):
        by_month = {m: 0.0 for m in range(1, 13)}
        by_month[6] = -10.0
        result = monthly_percentage(date(2026, 6, 1), by_month)
        self.assertEqual(result.month, 6)
        self.assertAlmostEqual(result.factor, 0.90)

    def test_missing_month_raises(self):
        with self.assertRaises(ValueError):
            monthly_percentage(date(2026, 12, 1), {m: 0.0 for m in range(1, 12)})  # missing December


class TestFixedOffset(TestCase):
    def test_offset_passed_through(self):
        self.assertAlmostEqual(fixed_offset(-12.5).offset, -12.5)


class TestEuropeanOption(TestCase):
    """
    Plan 22 section 6 Step C's test requirements: delta at known moneyness
    and tenor; varying as_of changes the result (the regression guard for
    D3); a delivery period before as_of is handled explicitly rather than
    silently becoming nan -> 0; portion and residual both returned and
    summing to 1 (of gross).
    """

    def test_deep_in_the_money_delta_approaches_one(self):
        result = european_option(
            price=2000.0, strike=500.0, as_of=date(2026, 1, 1),
            delivery_period=date(2027, 1, 1), volatility=0.30, rate=0.02, portion=0.0525,
        )
        self.assertGreater(result.delta, 0.9)

    def test_deep_out_of_the_money_delta_approaches_zero(self):
        result = european_option(
            price=50.0, strike=500.0, as_of=date(2026, 1, 1),
            delivery_period=date(2027, 1, 1), volatility=0.30, rate=0.02, portion=0.0525,
        )
        self.assertLess(result.delta, 0.1)

    def test_changing_as_of_changes_the_result(self):
        near = european_option(
            price=800.0, strike=500.0, as_of=date(2026, 12, 1),
            delivery_period=date(2027, 1, 1), volatility=0.30, rate=0.02, portion=0.0525,
        )
        far = european_option(
            price=800.0, strike=500.0, as_of=date(2025, 1, 1),
            delivery_period=date(2027, 1, 1), volatility=0.30, rate=0.02, portion=0.0525,
        )
        self.assertNotAlmostEqual(near.option_value, far.option_value)
        self.assertNotEqual(near.days_to_expiry, far.days_to_expiry)

    def test_delivery_period_before_as_of_is_intrinsic_not_nan(self):
        # in the money at expiry -> intrinsic value, delta exactly 1, no NaN anywhere
        itm = european_option(
            price=800.0, strike=500.0, as_of=date(2026, 6, 1),
            delivery_period=date(2026, 1, 1), volatility=0.30, rate=0.02, portion=0.0525,
        )
        self.assertLessEqual(itm.days_to_expiry, 0)
        self.assertEqual(itm.delta, 1.0)
        self.assertAlmostEqual(itm.option_value, 300.0)  # price - strike
        self.assertFalse(itm.delta != itm.delta)  # not NaN
        # out of the money at expiry -> zero value, delta exactly 0
        otm = european_option(
            price=300.0, strike=500.0, as_of=date(2026, 6, 1),
            delivery_period=date(2026, 1, 1), volatility=0.30, rate=0.02, portion=0.0525,
        )
        self.assertEqual(otm.delta, 0.0)
        self.assertEqual(otm.option_value, 0.0)

    def test_rebate_and_residual_fractions_sum_to_one(self):
        result = european_option(
            price=800.0, strike=500.0, as_of=date(2026, 1, 1),
            delivery_period=date(2027, 1, 1), volatility=0.30, rate=0.02, portion=0.0525,
        )
        self.assertAlmostEqual(result.rebate_fraction + result.residual_fraction, 1.0)

    def test_rebate_fraction_bounded_by_portion(self):
        # rebate_fraction = portion * delta, and delta in [0, 1], so
        # rebate_fraction can never exceed the configured portion.
        result = european_option(
            price=5000.0, strike=500.0, as_of=date(2026, 1, 1),
            delivery_period=date(2027, 1, 1), volatility=0.30, rate=0.02, portion=0.0525,
        )
        self.assertLessEqual(result.rebate_fraction, 0.0525 + 1e-9)


class TestAsianOption(TestCase):
    def test_delivery_period_before_as_of_is_intrinsic_not_nan(self):
        itm = asian_option(
            price=800.0, strike=500.0, as_of=date(2026, 6, 1),
            delivery_period=date(2026, 1, 1), volatility=0.30, rate=0.02, portion=0.05,
        )
        self.assertLessEqual(itm.days_to_expiry, 0)
        self.assertEqual(itm.delta, 1.0)
        self.assertFalse(itm.delta != itm.delta)

    def test_rebate_and_residual_fractions_sum_to_one(self):
        result = asian_option(
            price=800.0, strike=500.0, as_of=date(2026, 1, 1),
            delivery_period=date(2027, 1, 1), volatility=0.30, rate=0.02, portion=0.05,
        )
        self.assertAlmostEqual(result.rebate_fraction + result.residual_fraction, 1.0)
