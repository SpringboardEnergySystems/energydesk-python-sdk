"""
Typed wrapper for the `terms` JSON blob on DealVersion / ContractOffer /
StructuredContract. See energydesk/apps/origination/README.md ("terms JSON")
and energydesk/apps/origination/terms.py (RULE_KEYS, KNOWN_RULE_TYPES) for
the appserver-side definition this mirrors.

`terms` is intentionally open-ended: RULE_KEYS is a fixed vocabulary of slots,
but the allowed `type` per slot - and that type's parameters - are declared
per-ProductTemplate in `rule_schema` and validated server-side. A customer
can add a new template with a new rule `type` (or new params) without an
appserver code change, so the SDK does not attempt a closed discriminated
union of rule types here. `RuleObject` types the one thing that's fixed (a
`type` discriminator string) and passes every other field through untyped.

If you need strict validation of a specific rule shape client-side, read
`type` and branch - don't add new pydantic subclasses per type here, that
would re-introduce the closed vocabulary the appserver deliberately avoids.
"""
from __future__ import annotations

from typing import Any, Optional, Tuple

from pydantic import BaseModel, ConfigDict

# Fixed vocabulary of rule keys - keep in sync with
# energydesk/apps/origination/terms.py::RULE_KEYS.
RULE_KEYS: Tuple[str, ...] = (
    "volume",
    "price",
    "index",
    "shape",
    "imbalance",
    "goo",
    "curtailment",
    "negative_price",
    "settlement",
    "credit",
    "regulatory",
)

# Reference list of well-known types per key, for client-side hinting only -
# the appserver is authoritative (via ProductTemplate.rule_schema). Keep in
# sync with energydesk/apps/origination/terms.py::KNOWN_RULE_TYPES.
KNOWN_RULE_TYPES = {
    "volume": ("PAY_AS_PRODUCED", "PAY_AS_FORECAST", "FIXED_VOLUME", "FIXED_PROFILE", "LOAD_FOLLOWING", "BASELOAD"),
    "price": ("FIXED", "INDEXED", "FIXED_WITH_FLOOR", "COLLAR", "STEPPED", "FORMULA"),
    "index": ("NONE", "SPOT_AREA", "SPOT_SYSTEM", "MONTHLY_AVERAGE", "CUSTOM_BASIS"),
    "shape": ("AS_PRODUCED", "BASELOAD", "PROFILE", "SHAPED_BY_TABLE"),
    "imbalance": ("PRODUCER", "BUYER", "SHARED", "VOLUME_WEIGHTED"),
    "goo": ("NONE", "INCLUDED", "SEPARATE_PRICE", "BUYER_OPTION"),
    "curtailment": ("NONE", "BUYER_TAKES_VOLUME_RISK", "PRODUCER_TAKES_VOLUME_RISK", "COMPENSATED"),
    "negative_price": ("NONE", "STOP_PRODUCTION", "PRICE_FLOOR_ZERO", "PASS_THROUGH"),
    "settlement": ("MONTHLY", "QUARTERLY", "ANNUAL", "ON_DELIVERY"),
    "credit": ("NONE", "COLLATERAL_THRESHOLD", "PARENT_GUARANTEE", "PREPAYMENT"),
    "regulatory": ("NONE", "NO_FIXED_PRICE_2023"),
}


class RuleObject(BaseModel):
    """One entry in `terms`: a `type` discriminator plus free-form params.

    `type` is required (matching the appserver's own light validation: "rule
    must be an object with a 'type'"). Everything else is template-defined,
    so extra fields are allowed and preserved rather than rejected or dropped.
    """
    model_config = ConfigDict(extra="allow")

    type: str


class Terms(BaseModel):
    """The `terms` JSON blob: RULE_KEYS slots, each an optional RuleObject.

    Rules the template doesn't apply to a given deal are simply absent, so
    every field is Optional. Server-side validation against
    ProductTemplate.rule_schema is authoritative; this model only guarantees
    "if present, it's a dict with a type".
    """
    model_config = ConfigDict(extra="forbid")

    volume: Optional[RuleObject] = None
    price: Optional[RuleObject] = None
    index: Optional[RuleObject] = None
    shape: Optional[RuleObject] = None
    imbalance: Optional[RuleObject] = None
    goo: Optional[RuleObject] = None
    curtailment: Optional[RuleObject] = None
    negative_price: Optional[RuleObject] = None
    settlement: Optional[RuleObject] = None
    credit: Optional[RuleObject] = None
    regulatory: Optional[RuleObject] = None
