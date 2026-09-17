"""
Enums mirroring energydesk.apps.portfoliomanager multi-leg-deal lookups
(plans/multi_leg_deals.md, appserver PR #415 "DealPackage origination
completion" - DealPackage/PackageVersion models, multi-leg booking).

Values are string-identical to the Django-side choice values (not the
descriptions) so a client can round-trip a wire value straight into these
enums without a translation table. When the appserver adds a choice, add it
here too - these are additive-only mirrors, not independent vocabularies.

These four lookups have local fallback fixtures on the appserver side
(portfoliomanager/fixtures/{leg_role_types,contract_group_type_types,
group_fee_type_types,fee_allocation_types}.py) that import their
descriptions from this module when it's installed, falling back to a local
CHOICES tuple otherwise - once this module lands on develop and is
installed there, the appserver fixture reload picks these up automatically
with no appserver code change needed.

Note: GroupFeeTypeEnum is unrelated to the older, pre-existing exchange
fee-rate-schedule model also called FeeType in portfoliomanager -
GroupFeeType classifies bilateral-trading/origination fees (structuring,
origination, management, balancing service), a different domain. Do not
conflate the two.
"""
from enum import Enum


class LegRoleEnum(str, Enum):
    """Mirrors portfoliomanager.models.LEG_ROLE_CHOICES."""
    FIXED_PRICE = "FIXED_PRICE"
    FLOATING_PRICE = "FLOATING_PRICE"
    VOLUME_BLOCK = "VOLUME_BLOCK"
    CERTIFICATE = "CERTIFICATE"
    FINANCIAL_HEDGE = "FINANCIAL_HEDGE"
    FEE = "FEE"
    HEDGE = "HEDGE"


def leg_role_description(x: LegRoleEnum) -> str:
    return {
        LegRoleEnum.FIXED_PRICE: "Fixed price",
        LegRoleEnum.FLOATING_PRICE: "Floating price",
        LegRoleEnum.VOLUME_BLOCK: "Volume block",
        LegRoleEnum.CERTIFICATE: "Certificate",
        LegRoleEnum.FINANCIAL_HEDGE: "Financial hedge",
        LegRoleEnum.FEE: "Fee",
        LegRoleEnum.HEDGE: "Hedge (attached after booking)",
    }[x]


class ContractGroupTypeEnum(str, Enum):
    """Mirrors portfoliomanager.models.CONTRACT_GROUP_TYPE_CHOICES."""
    ORIGINATED_PACKAGE = "ORIGINATED_PACKAGE"
    HEDGED_STRUCTURE = "HEDGED_STRUCTURE"
    SYNTHETIC = "SYNTHETIC"
    MANUAL = "MANUAL"


def contract_group_type_description(x: ContractGroupTypeEnum) -> str:
    return {
        ContractGroupTypeEnum.ORIGINATED_PACKAGE: "Originated package",
        ContractGroupTypeEnum.HEDGED_STRUCTURE: "Hedged structure",
        ContractGroupTypeEnum.SYNTHETIC: "Synthetic",
        ContractGroupTypeEnum.MANUAL: "Manual",
    }[x]


class GroupFeeTypeEnum(str, Enum):
    """Mirrors portfoliomanager.models.GROUP_FEE_TYPE_CHOICES.

    Not a subtype of the older, unrelated exchange fee-rate-schedule
    FeeType model in portfoliomanager - see module docstring.
    """
    STRUCTURING = "STRUCTURING"
    ORIGINATION = "ORIGINATION"
    MANAGEMENT = "MANAGEMENT"
    BALANCING_SERVICE = "BALANCING_SERVICE"


def group_fee_type_description(x: GroupFeeTypeEnum) -> str:
    return {
        GroupFeeTypeEnum.STRUCTURING: "Structuring",
        GroupFeeTypeEnum.ORIGINATION: "Origination",
        GroupFeeTypeEnum.MANAGEMENT: "Management",
        GroupFeeTypeEnum.BALANCING_SERVICE: "Balancing service",
    }[x]


class FeeAllocationEnum(str, Enum):
    """Mirrors portfoliomanager.models.FEE_ALLOCATION_CHOICES."""
    GROUP_LEVEL = "GROUP_LEVEL"
    PRO_RATA_NOTIONAL = "PRO_RATA_NOTIONAL"
    PRO_RATA_VOLUME = "PRO_RATA_VOLUME"
    PRIMARY_CONTRACT = "PRIMARY_CONTRACT"


def fee_allocation_description(x: FeeAllocationEnum) -> str:
    return {
        FeeAllocationEnum.GROUP_LEVEL: "Group level",
        FeeAllocationEnum.PRO_RATA_NOTIONAL: "Pro rata notional",
        FeeAllocationEnum.PRO_RATA_VOLUME: "Pro rata volume",
        FeeAllocationEnum.PRIMARY_CONTRACT: "Primary contract",
    }[x]
