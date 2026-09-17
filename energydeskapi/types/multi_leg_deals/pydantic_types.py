"""
Typed wire payloads for energydesk.apps.origination's DealPackage /
PackageVersion endpoints (plans/multi_leg_deals.md, appserver PR #415
"DealPackage origination completion", merged - new DealPackage /
PackageVersion models, firm-offer/credit gates, multi-leg booking).

Read types (DealPackage, PackageVersion, Leg) mirror the actual wire shape
returned today, verified against
energydesk/apps/origination/interfaces/serializers.py on the merged PR:
DealPackageSerializer, PackageVersionSerializer, DealEmbeddedSerializer.

Leg is built from DealEmbeddedSerializer's *actual* field list, which does
not yet expose the leg_no/leg_role/account/package fields PR #415 added to
Deal - that's a probable appserver oversight (see this PR's description),
not modeled here since these types mirror the wire, not the aspiration.

Write types (CreatePackageWrite, AddLegWrite, PublishPackageOfferWrite)
mirror CreatePackageInput / AddLegInput / PublishPackageOfferInput.
PublishPackageOfferWrite deliberately has no `kind` field: the appserver's
quote/publish actions both validate PublishPackageOfferInput (so `kind` is
required or the request 400s) but then ignore the validated value and force
kind="INDICATIVE"/"FIRM" based on which URL was called
(restmodel.py::DealPackageViewSet._publish) - the SDK wrapper
(energydeskapi.origination.origination_api.OriginationApi.quote/publish)
injects the correct literal internally so this oddity never reaches SDK
callers.

Follows energydeskapi.types.agreements.pydantic_types's style
(pydantic.BaseModel, ConfigDict(extra="allow") for anything that mirrors a
JSON-ish or evolving server shape, plain required/Optional fields
otherwise).
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Leg(BaseModel):
    """Wire shape of a package leg (Deal) as returned by add_leg and by
    DealPackageEmbeddedSerializer's nested `legs` - i.e.
    DealEmbeddedSerializer's actual field list. Does NOT include
    leg_no/leg_role/account/package - Deal gained those FKs in PR #415 but
    DealEmbeddedSerializer's `fields` list was not updated to expose them
    (see module docstring / this PR's description)."""
    model_config = ConfigDict(extra="allow")

    pk: int
    reference: str
    title: str
    status: dict
    template: Optional[dict] = None
    counterpart: Optional[dict] = None
    buy_or_sell: Optional[str] = None
    trading_book: Optional[int] = None
    price_area: Optional[str] = None
    delivery_from: datetime
    delivery_until: datetime
    current_version: Optional[dict] = None
    contract: Optional[str] = None
    originator: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class PackageVersion(BaseModel):
    """Wire shape of GET origination/package-versions/{pk}/ (and the
    versions_list action) - mirrors PackageVersionSerializer. Read-only: a
    package version is immutable once created."""
    model_config = ConfigDict(extra="allow")

    pk: int
    package: str
    version_no: int
    label: Optional[str] = None
    leg_versions: Optional[dict] = None
    package_fees: Optional[dict] = None
    price_summary: Optional[dict] = None
    is_locked: bool = False
    comment: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime


class DealPackage(BaseModel):
    """Wire shape of GET/POST origination/packages/{pk}/ - mirrors
    DealPackageSerializer."""
    model_config = ConfigDict(extra="allow")

    pk: int
    reference: str
    title: str
    status: dict
    contract_owner: Optional[int] = None
    counterpart: Optional[dict] = None
    trading_book: Optional[int] = None
    account: Optional[int] = None
    current_version: Optional[str] = None
    contract_group: Optional[str] = None
    originator: Optional[int] = None
    updated_by: Optional[int] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CreatePackageWrite(BaseModel):
    """Mirrors CreatePackageInput."""
    model_config = ConfigDict(extra="allow")

    title: str = ""
    contract_owner: Optional[int] = None
    counterpart: Optional[int] = None
    trading_book: int
    account: Optional[int] = None
    source: str = ""
    notes: str = ""


class AddLegWrite(BaseModel):
    """Mirrors AddLegInput."""
    model_config = ConfigDict(extra="allow")

    template: int
    delivery_from: datetime
    delivery_until: datetime
    leg_role: Optional[int] = None
    title: str = ""
    commodity: Optional[int] = None
    price_area: Optional[str] = None
    asset: Optional[int] = None
    portfolio: Optional[int] = None
    buy_or_sell: Optional[str] = None


class PublishPackageOfferWrite(BaseModel):
    """Mirrors PublishPackageOfferInput, minus `kind` - see module
    docstring: the wrapper (OriginationApi.quote/publish) injects `kind`
    internally so callers never need to know about the appserver's
    validated-but-ignored `kind` oddity."""
    model_config = ConfigDict(extra="allow")

    offered_to: Optional[int] = None
    valid_until: datetime
    price_amount: Optional[Decimal] = None
    price_currency: str = "EUR"
