from unittest import TestCase

from energydeskapi.types.agreements import (
    AccountTypeEnum,
    AgreementStatusEnum,
    AgreementTypeEnum,
    CashflowKindEnum,
    CashflowStatusEnum,
    ConfirmationChannelEnum,
    ConfirmationStatusEnum,
    CreditProfile,
    CsaTypeEnum,
    DocumentSystemEnum,
    ElectionSheetLifted,
    InvoiceStatusEnum,
    InvoicingCadenceEnum,
    MasterAgreementSummary,
    ValuationFrequencyEnum,
    account_type_description,
    agreement_status_description,
    agreement_type_description,
    cashflow_kind_description,
    cashflow_status_description,
    confirmation_channel_description,
    confirmation_status_description,
    csa_type_description,
    document_system_description,
    invoice_status_description,
    invoicing_cadence_description,
    valuation_frequency_description,
)

# Wire-value snapshots of the appserver's frozen codes (already shipped in
# energydesk/apps/agreements/enums.py, step 1 of
# plans/customer_account_model.md) - a rename/removal on that side breaks
# this test instead of silently drifting. Keep in sync with that module.
DJANGO_ACCOUNT_TYPE_VALUES = {"COUNTERPARTY", "END_CUSTOMER", "INTRA_GROUP"}
DJANGO_AGREEMENT_TYPE_VALUES = {
    "EFET_POWER", "EFET_GAS", "ISDA", "PPA_FRAMEWORK", "SUPPLY_TERMS", "INTRA_GROUP", "BESPOKE",
}
DJANGO_AGREEMENT_STATUS_VALUES = {"DRAFT", "EXECUTED", "SUSPENDED", "TERMINATED"}
DJANGO_INVOICING_CADENCE_VALUES = {"MONTHLY", "QUARTERLY"}
DJANGO_DOCUMENT_SYSTEM_VALUES = {"ENERGYDESK", "SHAREPOINT", "OTHER"}
DJANGO_CSA_TYPE_VALUES = {"EFET_CSA", "ISDA_CSA", "BESPOKE", "PARENT_GUARANTEE", "BANK_GUARANTEE"}
DJANGO_VALUATION_FREQUENCY_VALUES = {"DAILY", "WEEKLY", "MONTHLY"}


class TestEnumsMirrorDjangoChoices(TestCase):
    def test_account_type_enum_matches_django(self):
        self.assertEqual({e.value for e in AccountTypeEnum}, DJANGO_ACCOUNT_TYPE_VALUES)

    def test_agreement_type_enum_matches_django(self):
        self.assertEqual({e.value for e in AgreementTypeEnum}, DJANGO_AGREEMENT_TYPE_VALUES)

    def test_agreement_status_enum_matches_django(self):
        self.assertEqual({e.value for e in AgreementStatusEnum}, DJANGO_AGREEMENT_STATUS_VALUES)

    def test_invoicing_cadence_enum_matches_django(self):
        self.assertEqual({e.value for e in InvoicingCadenceEnum}, DJANGO_INVOICING_CADENCE_VALUES)

    def test_document_system_enum_matches_django(self):
        self.assertEqual({e.value for e in DocumentSystemEnum}, DJANGO_DOCUMENT_SYSTEM_VALUES)

    def test_csa_type_enum_matches_django(self):
        self.assertEqual({e.value for e in CsaTypeEnum}, DJANGO_CSA_TYPE_VALUES)

    def test_valuation_frequency_enum_matches_django(self):
        self.assertEqual({e.value for e in ValuationFrequencyEnum}, DJANGO_VALUATION_FREQUENCY_VALUES)

    def test_every_enum_value_has_a_description(self):
        for e in AccountTypeEnum:
            self.assertIsInstance(account_type_description(e), str)
        for e in AgreementTypeEnum:
            self.assertIsInstance(agreement_type_description(e), str)
        for e in AgreementStatusEnum:
            self.assertIsInstance(agreement_status_description(e), str)
        for e in InvoicingCadenceEnum:
            self.assertIsInstance(invoicing_cadence_description(e), str)
        for e in DocumentSystemEnum:
            self.assertIsInstance(document_system_description(e), str)
        for e in CsaTypeEnum:
            self.assertIsInstance(csa_type_description(e), str)
        for e in ValuationFrequencyEnum:
            self.assertIsInstance(valuation_frequency_description(e), str)
        for e in ConfirmationStatusEnum:
            self.assertIsInstance(confirmation_status_description(e), str)
        for e in ConfirmationChannelEnum:
            self.assertIsInstance(confirmation_channel_description(e), str)
        for e in CashflowKindEnum:
            self.assertIsInstance(cashflow_kind_description(e), str)
        for e in CashflowStatusEnum:
            self.assertIsInstance(cashflow_status_description(e), str)
        for e in InvoiceStatusEnum:
            self.assertIsInstance(invoice_status_description(e), str)


class TestElectionSheetLifted(TestCase):
    def test_parses_a_realistic_payload(self):
        raw = {
            "schema_version": "1.0",
            "early_termination_automatic": False,
            "material_reason_credit_event": True,
            "cross_default_threshold_amount": 5_000_000.0,
            "cross_default_threshold_currency": "EUR",
            "tangible_net_worth_threshold": 10_000_000.0,
            "floating_price_fallback": "SPOT_AREA",
            "vat_treatment": "STANDARD",
            "expert_determination": False,
            "elections": {"§7": {"choice": "A"}},
        }
        sheet = ElectionSheetLifted(**raw)
        self.assertEqual(sheet.cross_default_threshold_currency, "EUR")
        self.assertEqual(sheet.model_dump()["elections"], {"§7": {"choice": "A"}})

    def test_defaults_when_only_schema_version_given(self):
        sheet = ElectionSheetLifted(schema_version="1.0")
        self.assertFalse(sheet.early_termination_automatic)
        self.assertTrue(sheet.material_reason_credit_event)
        self.assertIsNone(sheet.cross_default_threshold_amount)


class TestCreditProfile(TestCase):
    def test_parses_a_full_profile(self):
        raw = {
            "as_of": "2026-09-12T09:00:00Z",
            "rating_code": "A2",
            "rating_category_tier": 1,
            "risk_limits": {"pfe": 5_000_000.0, "cash_amount": 1_000_000.0, "contract_tenor": 3.0, "contract_volume": 500_000.0},
            "risk_limits_source": "CATEGORY_DEFAULT",
            "allowed_counterpart_types": ["TRADING_COMPANY", "BANK"],
            "volume_limit_mwh": 250_000.0,
            "has_annual_accounts": True,
        }
        profile = CreditProfile(**raw)
        self.assertEqual(profile.risk_limits.pfe, 5_000_000.0)
        self.assertEqual(profile.allowed_counterpart_types, ["TRADING_COMPANY", "BANK"])

    def test_parses_a_profile_with_no_rating(self):
        raw = {
            "as_of": "2026-09-12T09:00:00Z",
            "rating_code": None,
            "rating_category_tier": None,
            "risk_limits": None,
            "risk_limits_source": None,
            "allowed_counterpart_types": [],
            "volume_limit_mwh": None,
            "has_annual_accounts": False,
        }
        profile = CreditProfile(**raw)
        self.assertIsNone(profile.risk_limits)
        self.assertEqual(profile.allowed_counterpart_types, [])


class TestMasterAgreementSummary(TestCase):
    def test_parses_a_realistic_payload(self):
        raw = {
            "pk": 42,
            "reference": "MA-ENT-STATKRAFT-2026",
            "title": "EFET Power - Entelios / Statkraft",
            "agreement_type": "EFET_POWER",
            "status": "EXECUTED",
            "account_reference": "ACC-ENT-00412",
            "effective_date": "2026-01-01",
            "termination_date": None,
            "is_external_record": False,
        }
        summary = MasterAgreementSummary(**raw)
        self.assertEqual(summary.agreement_type, "EFET_POWER")
        self.assertIsNone(summary.termination_date)
