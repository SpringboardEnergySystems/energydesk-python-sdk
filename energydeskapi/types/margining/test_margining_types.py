from unittest import TestCase

from pydantic import ValidationError

from energydeskapi.types.margining import (
    AmortizationTypeEnum,
    CollateralAssetEmbedded,
    CollateralAssetTypeEnum,
    CollateralAssetWrite,
    CollateralDirectionEnum,
    CollateralMovementWrite,
    MarginAccountEmbedded,
    MarginAccountKindEnum,
    MarginCallStatusEnum,
    MarginCallWrite,
    MarginComponentEnum,
    MarginRequirementWrite,
    MarginSourceEnum,
    amortization_type_description,
    collateral_asset_type_description,
    collateral_direction_description,
    margin_account_kind_description,
    margin_call_status_description,
    margin_component_description,
    margin_source_description,
)

# Vocabulary taken verbatim from plans/customer_account_model.md's "Margin
# model" section - keep in sync if the plan changes before step 3 ships.
MARGIN_ACCOUNT_KIND_VALUES = {"BILATERAL_CSA", "CCP_CLEARED"}
MARGIN_COMPONENT_VALUES = {"INITIAL", "VARIATION", "ADDITIONAL", "TOTAL"}
MARGIN_SOURCE_VALUES = {"GCM_STATEMENT", "CALCULATED_CLEARED", "CALCULATED_BILATERAL", "FORECAST"}
MARGIN_CALL_STATUS_VALUES = {"OPEN", "DISPUTED", "SETTLED", "PARTIAL"}
COLLATERAL_ASSET_TYPE_VALUES = {"CASH", "BANK_GUARANTEE", "LETTER_OF_CREDIT", "PARENT_GUARANTEE", "BOND"}
COLLATERAL_DIRECTION_VALUES = {"POSTED", "RECEIVED"}
AMORTIZATION_TYPE_VALUES = {"NONE", "LINEAR", "SCHEDULE"}


class TestEnumsMatchThePlan(TestCase):
    def test_margin_account_kind_enum(self):
        self.assertEqual({e.value for e in MarginAccountKindEnum}, MARGIN_ACCOUNT_KIND_VALUES)

    def test_margin_component_enum(self):
        self.assertEqual({e.value for e in MarginComponentEnum}, MARGIN_COMPONENT_VALUES)

    def test_margin_source_enum(self):
        self.assertEqual({e.value for e in MarginSourceEnum}, MARGIN_SOURCE_VALUES)

    def test_margin_call_status_enum(self):
        self.assertEqual({e.value for e in MarginCallStatusEnum}, MARGIN_CALL_STATUS_VALUES)

    def test_collateral_asset_type_enum(self):
        self.assertEqual({e.value for e in CollateralAssetTypeEnum}, COLLATERAL_ASSET_TYPE_VALUES)

    def test_collateral_direction_enum(self):
        self.assertEqual({e.value for e in CollateralDirectionEnum}, COLLATERAL_DIRECTION_VALUES)

    def test_amortization_type_enum(self):
        self.assertEqual({e.value for e in AmortizationTypeEnum}, AMORTIZATION_TYPE_VALUES)

    def test_every_enum_value_has_a_description(self):
        for e in MarginAccountKindEnum:
            self.assertIsInstance(margin_account_kind_description(e), str)
        for e in MarginComponentEnum:
            self.assertIsInstance(margin_component_description(e), str)
        for e in MarginSourceEnum:
            self.assertIsInstance(margin_source_description(e), str)
        for e in MarginCallStatusEnum:
            self.assertIsInstance(margin_call_status_description(e), str)
        for e in CollateralAssetTypeEnum:
            self.assertIsInstance(collateral_asset_type_description(e), str)
        for e in CollateralDirectionEnum:
            self.assertIsInstance(collateral_direction_description(e), str)
        for e in AmortizationTypeEnum:
            self.assertIsInstance(amortization_type_description(e), str)


class TestMarginAccountEmbedded(TestCase):
    def test_parses_a_bilateral_account(self):
        raw = {
            "pk": 7,
            "reference": "MGN-ENT-00412",
            "kind": "BILATERAL_CSA",
            "owner_company_pk": 3,
            "external_account_id": None,
            "external_master_account": None,
            "trading_book_pks": [11, 12],
            "base_currency": "EUR",
            "is_active": True,
            "csa_threshold_amount": 500_000.0,
            "csa_independent_amount": 0.0,
            "csa_mta": 50_000.0,
            "payment_netting": True,
        }
        account = MarginAccountEmbedded(**raw)
        self.assertEqual(account.kind, "BILATERAL_CSA")
        self.assertEqual(account.trading_book_pks, [11, 12])

    def test_parses_a_cleared_account_with_no_csa_fields(self):
        raw = {
            "pk": 9,
            "reference": "MGN-HAF-SEB-01",
            "kind": "CCP_CLEARED",
            "owner_company_pk": 4,
            "trading_book_pks": [],
            "base_currency": "NOK",
        }
        account = MarginAccountEmbedded(**raw)
        self.assertIsNone(account.csa_threshold_amount)
        self.assertIsNone(account.payment_netting)


class TestCollateralAssetWrite(TestCase):
    def test_minimal_collateral_asset_has_no_new_fields_set(self):
        raw = {
            "account": 7,
            "asset_type": "CASH",
            "nominal_amount": 500_000.0,
            "currency": "EUR",
        }
        asset = CollateralAssetWrite(**raw)
        self.assertIsNone(asset.direction)
        self.assertIsNone(asset.amortization_type)
        self.assertIsNone(asset.amortization_schedule)
        self.assertIsNone(asset.linked_asset)
        self.assertIsNone(asset.notional_percent)

    def test_posted_amortising_guarantee_with_schedule(self):
        raw = {
            "account": 7,
            "asset_type": "PARENT_GUARANTEE",
            "nominal_amount": 3_000_000.0,
            "currency": "EUR",
            "direction": "POSTED",
            "amortization_type": "SCHEDULE",
            "amortization_schedule": [{"date": "2027-06-01", "remaining_pct": 66.67}],
            "linked_asset": 42,
            "notional_percent": 30.0,
        }
        asset = CollateralAssetWrite(**raw)
        self.assertEqual(asset.direction, "POSTED")
        self.assertEqual(asset.amortization_type, "SCHEDULE")
        self.assertEqual(len(asset.amortization_schedule), 1)
        self.assertEqual(asset.amortization_schedule[0].remaining_pct, 66.67)
        self.assertEqual(asset.linked_asset, 42)

    def test_received_cash_round_trips_through_embedded(self):
        raw = {
            "pk": 91,
            "account": 7,
            "asset_type": "CASH",
            "nominal_amount": 100_000.0,
            "currency": "EUR",
            "direction": "RECEIVED",
        }
        asset = CollateralAssetEmbedded(**raw)
        self.assertEqual(asset.pk, 91)
        self.assertEqual(asset.direction, "RECEIVED")

    def test_missing_required_field_rejected(self):
        with self.assertRaises(ValidationError):
            CollateralAssetWrite(asset_type="CASH", nominal_amount=1.0, currency="EUR")


class TestWriteTypes(TestCase):
    def test_margin_requirement_write_round_trips(self):
        raw = {
            "account": 7,
            "as_of": "2026-09-12",
            "component": "INITIAL",
            "source": "CALCULATED_BILATERAL",
            "amount": 123456.78,
            "currency": "EUR",
            "computed_at": "2026-09-12T06:00:00Z",
            "calculated_by": "clearing-service-1.4.0",
        }
        req = MarginRequirementWrite(**raw)
        self.assertEqual(req.component, "INITIAL")
        self.assertIsNone(req.forecast_run_ref)

    def test_margin_requirement_write_forecast_variant(self):
        raw = {
            "account": 7,
            "as_of": "2026-09-12",
            "component": "TOTAL",
            "source": "FORECAST",
            "amount": 200000.0,
            "currency": "EUR",
            "forecast_run_ref": "run-2026-09-12-001",
            "forecast_for_date": "2026-10-01",
            "p50_amount": 190000.0,
            "p95_amount": 240000.0,
            "p99_amount": 260000.0,
            "computed_at": "2026-09-12T06:00:00Z",
            "calculated_by": "clearing-service-1.4.0",
        }
        req = MarginRequirementWrite(**raw)
        self.assertEqual(req.forecast_run_ref, "run-2026-09-12-001")
        self.assertEqual(req.p95_amount, 240000.0)

    def test_margin_call_write_round_trips(self):
        raw = {
            "account": 7,
            "direction": "RECEIVED",
            "call_date": "2026-09-12",
            "due_at": "2026-09-15T12:00:00Z",
            "amount": 50000.0,
            "currency": "EUR",
            "status": "OPEN",
        }
        call = MarginCallWrite(**raw)
        self.assertEqual(call.status, "OPEN")
        self.assertIsNone(call.requirement)

    def test_collateral_movement_write_round_trips(self):
        raw = {
            "account": 7,
            "movement_date": "2026-09-12",
            "direction": "POST",
            "amount": 50000.0,
            "currency": "EUR",
        }
        movement = CollateralMovementWrite(**raw)
        self.assertEqual(movement.direction, "POST")
        self.assertIsNone(movement.asset)
