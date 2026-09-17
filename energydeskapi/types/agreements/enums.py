"""
Enums mirroring energydesk.apps.agreements choices.

Values are string-identical to the Django-side choice values (not the
descriptions) so a client can round-trip a wire value straight into these
enums without a translation table. When the appserver adds a choice, add it
here too - these are additive-only mirrors, not independent vocabularies.

AccountTypeEnum through ValuationFrequencyEnum mirror lookup tables already
shipped in the appserver (energydesk/apps/agreements/enums.py, step 1 of
plans/customer_account_model.md) - those codes are frozen, this module must
match them exactly. ConfirmationStatusEnum through InvoiceStatusEnum mirror
step 3 (Confirmation / CashflowItem / Invoice), not yet built in the
appserver - this SDK PR is where that vocabulary is decided.
"""
from enum import Enum


class AccountTypeEnum(str, Enum):
    COUNTERPARTY = "COUNTERPARTY"
    END_CUSTOMER = "END_CUSTOMER"
    INTRA_GROUP = "INTRA_GROUP"


def account_type_description(x: AccountTypeEnum) -> str:
    return {
        AccountTypeEnum.COUNTERPARTY: "Counterparty",
        AccountTypeEnum.END_CUSTOMER: "End customer",
        AccountTypeEnum.INTRA_GROUP: "Intra-group",
    }[x]


class AgreementTypeEnum(str, Enum):
    EFET_POWER = "EFET_POWER"
    EFET_GAS = "EFET_GAS"
    ISDA = "ISDA"
    PPA_FRAMEWORK = "PPA_FRAMEWORK"
    SUPPLY_TERMS = "SUPPLY_TERMS"
    INTRA_GROUP = "INTRA_GROUP"
    BESPOKE = "BESPOKE"


def agreement_type_description(x: AgreementTypeEnum) -> str:
    return {
        AgreementTypeEnum.EFET_POWER: "EFET General Agreement (Power)",
        AgreementTypeEnum.EFET_GAS: "EFET General Agreement (Gas)",
        AgreementTypeEnum.ISDA: "ISDA Master Agreement",
        AgreementTypeEnum.PPA_FRAMEWORK: "PPA framework agreement",
        AgreementTypeEnum.SUPPLY_TERMS: "Retail / B2B supply terms",
        AgreementTypeEnum.INTRA_GROUP: "Intra-group agreement",
        AgreementTypeEnum.BESPOKE: "Bespoke agreement",
    }[x]


class AgreementStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    EXECUTED = "EXECUTED"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"


def agreement_status_description(x: AgreementStatusEnum) -> str:
    return {
        AgreementStatusEnum.DRAFT: "Draft",
        AgreementStatusEnum.EXECUTED: "Executed",
        AgreementStatusEnum.SUSPENDED: "Suspended",
        AgreementStatusEnum.TERMINATED: "Terminated",
    }[x]


class InvoicingCadenceEnum(str, Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"


def invoicing_cadence_description(x: InvoicingCadenceEnum) -> str:
    return {
        InvoicingCadenceEnum.MONTHLY: "Monthly",
        InvoicingCadenceEnum.QUARTERLY: "Quarterly",
    }[x]


class DocumentSystemEnum(str, Enum):
    ENERGYDESK = "ENERGYDESK"
    SHAREPOINT = "SHAREPOINT"
    OTHER = "OTHER"


def document_system_description(x: DocumentSystemEnum) -> str:
    return {
        DocumentSystemEnum.ENERGYDESK: "EnergyDesk",
        DocumentSystemEnum.SHAREPOINT: "SharePoint",
        DocumentSystemEnum.OTHER: "Other / external",
    }[x]


class CsaTypeEnum(str, Enum):
    EFET_CSA = "EFET_CSA"
    ISDA_CSA = "ISDA_CSA"
    BESPOKE = "BESPOKE"
    PARENT_GUARANTEE = "PARENT_GUARANTEE"
    BANK_GUARANTEE = "BANK_GUARANTEE"


def csa_type_description(x: CsaTypeEnum) -> str:
    return {
        CsaTypeEnum.EFET_CSA: "EFET Credit Support Annex",
        CsaTypeEnum.ISDA_CSA: "ISDA Credit Support Annex",
        CsaTypeEnum.BESPOKE: "Bespoke collateral terms",
        CsaTypeEnum.PARENT_GUARANTEE: "Parent guarantee",
        CsaTypeEnum.BANK_GUARANTEE: "Bank guarantee",
    }[x]


class ValuationFrequencyEnum(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


def valuation_frequency_description(x: ValuationFrequencyEnum) -> str:
    return {
        ValuationFrequencyEnum.DAILY: "Daily",
        ValuationFrequencyEnum.WEEKLY: "Weekly",
        ValuationFrequencyEnum.MONTHLY: "Monthly",
    }[x]


class ConfirmationStatusEnum(str, Enum):
    """Mirrors the not-yet-built agreements.Confirmation.status (step 3)."""
    PENDING = "PENDING"
    SENT = "SENT"
    RECEIVED = "RECEIVED"
    MATCHED = "MATCHED"
    DISPUTED = "DISPUTED"
    BROKER_CONFIRMED = "BROKER_CONFIRMED"
    WAIVED = "WAIVED"


def confirmation_status_description(x: ConfirmationStatusEnum) -> str:
    return {
        ConfirmationStatusEnum.PENDING: "Pending",
        ConfirmationStatusEnum.SENT: "Sent",
        ConfirmationStatusEnum.RECEIVED: "Received",
        ConfirmationStatusEnum.MATCHED: "Matched",
        ConfirmationStatusEnum.DISPUTED: "Disputed",
        ConfirmationStatusEnum.BROKER_CONFIRMED: "Broker confirmed",
        ConfirmationStatusEnum.WAIVED: "Waived",
    }[x]


class ConfirmationChannelEnum(str, Enum):
    ECM = "ECM"
    EMAIL = "EMAIL"
    BROKER = "BROKER"
    CONNECT = "CONNECT"
    MANUAL = "MANUAL"


def confirmation_channel_description(x: ConfirmationChannelEnum) -> str:
    return {
        ConfirmationChannelEnum.ECM: "Electronic confirmation matching",
        ConfirmationChannelEnum.EMAIL: "Email",
        ConfirmationChannelEnum.BROKER: "Broker",
        ConfirmationChannelEnum.CONNECT: "Connect",
        ConfirmationChannelEnum.MANUAL: "Manual",
    }[x]


class CashflowKindEnum(str, Enum):
    ENERGY = "ENERGY"
    GOO = "GOO"
    IMBALANCE = "IMBALANCE"
    FEE = "FEE"
    COLLATERAL = "COLLATERAL"
    TERMINATION = "TERMINATION"


def cashflow_kind_description(x: CashflowKindEnum) -> str:
    return {
        CashflowKindEnum.ENERGY: "Energy",
        CashflowKindEnum.GOO: "Guarantee of Origin",
        CashflowKindEnum.IMBALANCE: "Imbalance",
        CashflowKindEnum.FEE: "Fee",
        CashflowKindEnum.COLLATERAL: "Collateral",
        CashflowKindEnum.TERMINATION: "Termination",
    }[x]


class CashflowStatusEnum(str, Enum):
    PROJECTED = "PROJECTED"
    DUE = "DUE"
    INVOICED = "INVOICED"
    PAID = "PAID"
    DISPUTED = "DISPUTED"


def cashflow_status_description(x: CashflowStatusEnum) -> str:
    return {
        CashflowStatusEnum.PROJECTED: "Projected",
        CashflowStatusEnum.DUE: "Due",
        CashflowStatusEnum.INVOICED: "Invoiced",
        CashflowStatusEnum.PAID: "Paid",
        CashflowStatusEnum.DISPUTED: "Disputed",
    }[x]


class InvoiceStatusEnum(str, Enum):
    """Not specified in plans/customer_account_model.md - this SDK PR is
    where the vocabulary is decided (standard invoice lifecycle)."""
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    DISPUTED = "DISPUTED"
    CANCELLED = "CANCELLED"


def invoice_status_description(x: InvoiceStatusEnum) -> str:
    return {
        InvoiceStatusEnum.DRAFT: "Draft",
        InvoiceStatusEnum.ISSUED: "Issued",
        InvoiceStatusEnum.PAID: "Paid",
        InvoiceStatusEnum.OVERDUE: "Overdue",
        InvoiceStatusEnum.DISPUTED: "Disputed",
        InvoiceStatusEnum.CANCELLED: "Cancelled",
    }[x]
