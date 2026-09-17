"""
Enums for the margin record tables (plans/customer_account_model.md,
"Margin model" section - MarginAccount / MarginRequirement / MarginCall /
CollateralAsset / CollateralMovement). None of these tables exist in the
appserver yet (step 3); this SDK PR is where the vocabulary is decided,
taken verbatim from the plan's model listing.
"""
from enum import Enum


class MarginAccountKindEnum(str, Enum):
    BILATERAL_CSA = "BILATERAL_CSA"
    CCP_CLEARED = "CCP_CLEARED"


def margin_account_kind_description(x: MarginAccountKindEnum) -> str:
    return {
        MarginAccountKindEnum.BILATERAL_CSA: "Bilateral (CSA)",
        MarginAccountKindEnum.CCP_CLEARED: "CCP cleared",
    }[x]


class MarginComponentEnum(str, Enum):
    INITIAL = "INITIAL"
    VARIATION = "VARIATION"
    ADDITIONAL = "ADDITIONAL"
    TOTAL = "TOTAL"


def margin_component_description(x: MarginComponentEnum) -> str:
    return {
        MarginComponentEnum.INITIAL: "Initial margin",
        MarginComponentEnum.VARIATION: "Variation margin",
        MarginComponentEnum.ADDITIONAL: "Additional (add-on)",
        MarginComponentEnum.TOTAL: "Total",
    }[x]


class MarginSourceEnum(str, Enum):
    GCM_STATEMENT = "GCM_STATEMENT"
    CALCULATED_CLEARED = "CALCULATED_CLEARED"
    CALCULATED_BILATERAL = "CALCULATED_BILATERAL"
    FORECAST = "FORECAST"


def margin_source_description(x: MarginSourceEnum) -> str:
    return {
        MarginSourceEnum.GCM_STATEMENT: "GCM statement",
        MarginSourceEnum.CALCULATED_CLEARED: "Calculated (cleared)",
        MarginSourceEnum.CALCULATED_BILATERAL: "Calculated (bilateral)",
        MarginSourceEnum.FORECAST: "Forecast",
    }[x]


class MarginCallStatusEnum(str, Enum):
    OPEN = "OPEN"
    DISPUTED = "DISPUTED"
    SETTLED = "SETTLED"
    PARTIAL = "PARTIAL"


def margin_call_status_description(x: MarginCallStatusEnum) -> str:
    return {
        MarginCallStatusEnum.OPEN: "Open",
        MarginCallStatusEnum.DISPUTED: "Disputed",
        MarginCallStatusEnum.SETTLED: "Settled",
        MarginCallStatusEnum.PARTIAL: "Partially settled",
    }[x]


class CollateralAssetTypeEnum(str, Enum):
    CASH = "CASH"
    BANK_GUARANTEE = "BANK_GUARANTEE"
    LETTER_OF_CREDIT = "LETTER_OF_CREDIT"
    PARENT_GUARANTEE = "PARENT_GUARANTEE"
    BOND = "BOND"


def collateral_asset_type_description(x: CollateralAssetTypeEnum) -> str:
    return {
        CollateralAssetTypeEnum.CASH: "Cash",
        CollateralAssetTypeEnum.BANK_GUARANTEE: "Bank guarantee",
        CollateralAssetTypeEnum.LETTER_OF_CREDIT: "Letter of credit",
        CollateralAssetTypeEnum.PARENT_GUARANTEE: "Parent guarantee",
        CollateralAssetTypeEnum.BOND: "Bond",
    }[x]
