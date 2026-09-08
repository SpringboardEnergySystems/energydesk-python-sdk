"""
Enums mirroring energydesk.apps.origination / portfoliomanager choices.

Values are string-identical to the Django-side choice values (not the
descriptions) so a client can round-trip a wire value straight into these
enums without a translation table. When the appserver adds a choice, add it
here too - these are additive-only mirrors, not independent vocabularies.
"""
from enum import Enum


class ContractFamilyEnum(str, Enum):
    """Mirrors portfoliomanager.models.CONTRACT_FAMILY_CHOICES."""
    STANDARD = "STANDARD"
    FINANCIAL_BILATERAL = "FINANCIAL_BILATERAL"
    PHYSICAL_STRUCTURED = "PHYSICAL_STRUCTURED"
    CERTIFICATE = "CERTIFICATE"
    CAPACITY = "CAPACITY"
    FX = "FX"
    TRANSFER = "TRANSFER"


def contract_family_description(x: ContractFamilyEnum) -> str:
    return {
        ContractFamilyEnum.STANDARD: "Standard",
        ContractFamilyEnum.FINANCIAL_BILATERAL: "Financial bilateral",
        ContractFamilyEnum.PHYSICAL_STRUCTURED: "Physical structured",
        ContractFamilyEnum.CERTIFICATE: "Certificate",
        ContractFamilyEnum.CAPACITY: "Capacity",
        ContractFamilyEnum.FX: "FX",
        ContractFamilyEnum.TRANSFER: "Transfer",
    }[x]


class DealStatusEnum(str, Enum):
    """Mirrors origination.models.DEAL_STATUS_CHOICES (and DEAL_TRANSITIONS)."""
    DRAFT = "DRAFT"
    IN_APPROVAL = "IN_APPROVAL"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"          # firm offer live at counterpart (Connect)
    NEGOTIATING = "NEGOTIATING"      # counterpart countered
    ACCEPTED = "ACCEPTED"            # counterpart accepted, not yet booked
    CONTRACTED = "CONTRACTED"        # Contract + satellites created
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


def deal_status_description(x: DealStatusEnum) -> str:
    return {
        DealStatusEnum.DRAFT: "Draft",
        DealStatusEnum.IN_APPROVAL: "In approval",
        DealStatusEnum.APPROVED: "Approved",
        DealStatusEnum.PUBLISHED: "Published",
        DealStatusEnum.NEGOTIATING: "Negotiating",
        DealStatusEnum.ACCEPTED: "Accepted",
        DealStatusEnum.CONTRACTED: "Contracted",
        DealStatusEnum.DECLINED: "Declined",
        DealStatusEnum.EXPIRED: "Expired",
        DealStatusEnum.CANCELLED: "Cancelled",
    }[x]


class OfferKindEnum(str, Enum):
    """Mirrors origination.models.OFFER_KIND_CHOICES."""
    INDICATIVE = "INDICATIVE"
    FIRM = "FIRM"


def offer_kind_description(x: OfferKindEnum) -> str:
    return {
        OfferKindEnum.INDICATIVE: "Indicative (quote)",
        OfferKindEnum.FIRM: "Firm (binding, acceptable in Connect)",
    }[x]


class OfferStatusEnum(str, Enum):
    """Mirrors origination.models.OFFER_STATUS_CHOICES.

    Note: this is PUBLISHED/VIEWED, not a single "OPEN" state - an offer is
    open (acceptable) while status is PUBLISHED or VIEWED and valid_until
    hasn't passed. See ContractOffer.is_open / is_acceptable.
    """
    PUBLISHED = "PUBLISHED"
    VIEWED = "VIEWED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    COUNTERED = "COUNTERED"
    EXPIRED = "EXPIRED"
    WITHDRAWN = "WITHDRAWN"


def offer_status_description(x: OfferStatusEnum) -> str:
    return {
        OfferStatusEnum.PUBLISHED: "Published",
        OfferStatusEnum.VIEWED: "Viewed",
        OfferStatusEnum.ACCEPTED: "Accepted",
        OfferStatusEnum.DECLINED: "Declined",
        OfferStatusEnum.COUNTERED: "Countered",
        OfferStatusEnum.EXPIRED: "Expired",
        OfferStatusEnum.WITHDRAWN: "Withdrawn",
    }[x]


#: Offer statuses that mean an offer can still be acted on (mirrors
#: ContractOffer.is_open on the appserver).
OPEN_OFFER_STATUSES = (OfferStatusEnum.PUBLISHED, OfferStatusEnum.VIEWED)


class ApprovalDecisionEnum(str, Enum):
    """Mirrors origination.models.APPROVAL_CHOICES (DealApproval.decision)."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


def approval_decision_description(x: ApprovalDecisionEnum) -> str:
    return {
        ApprovalDecisionEnum.PENDING: "Pending",
        ApprovalDecisionEnum.APPROVED: "Approved",
        ApprovalDecisionEnum.REJECTED: "Rejected",
        ApprovalDecisionEnum.WITHDRAWN: "Withdrawn",
    }[x]
