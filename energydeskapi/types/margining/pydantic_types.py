"""
Typed wire payloads for the margin record (plans/customer_account_model.md,
"Margin model" - MarginAccount / MarginRequirement / MarginCall /
CollateralAsset / CollateralMovement, none built in the appserver yet).

MarginAccountEmbedded is a read model: the account plus the resolved CSA
terms the clearing service needs (threshold/independent amount/MTA come
from CreditSupportAnnex, or CsaThresholdSchedule for the counterpart's
current rating tier if set - "the clearing service reads the resolved
threshold from the margin-account endpoint, never from creditrisk
directly").

The *Write types are what the clearing service POSTs back after a
calculation run - see the plan's "Repos and ownership" / "What the
clearing service needs from the appserver" tables. Batch POST bodies are
lists of these.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class MarginAccountEmbedded(BaseModel):
    model_config = ConfigDict(extra="allow")

    pk: int
    reference: str
    kind: str                              # MarginAccountKindEnum code
    owner_company_pk: int
    external_account_id: Optional[str] = None
    external_master_account: Optional[str] = None
    trading_book_pks: List[int] = []
    base_currency: str
    is_active: bool = True

    # Resolved CSA terms (bilateral accounts only; None for CCP_CLEARED)
    csa_threshold_amount: Optional[float] = None
    csa_independent_amount: Optional[float] = None
    csa_mta: Optional[float] = None
    payment_netting: Optional[bool] = None


class MarginRequirementWrite(BaseModel):
    model_config = ConfigDict(extra="allow")

    account: int                           # MarginAccount pk
    as_of: date
    component: str                         # MarginComponentEnum code
    source: str                            # MarginSourceEnum code
    amount: float
    currency: str
    forecast_run_ref: Optional[str] = None
    forecast_for_date: Optional[date] = None
    p50_amount: Optional[float] = None
    p95_amount: Optional[float] = None
    p99_amount: Optional[float] = None
    computed_at: datetime
    calculated_by: str
    detail_ref: Optional[str] = None


class MarginCallWrite(BaseModel):
    model_config = ConfigDict(extra="allow")

    account: int                           # MarginAccount pk
    direction: str                         # "RECEIVED" | "ISSUED"
    call_date: date
    due_at: datetime
    amount: float
    currency: str
    status: str                            # MarginCallStatusEnum code
    requirement: Optional[int] = None              # MarginRequirement pk
    forecast_requirement: Optional[int] = None     # MarginRequirement pk
    external_reference: Optional[str] = None


class CollateralMovementWrite(BaseModel):
    model_config = ConfigDict(extra="allow")

    account: int                           # MarginAccount pk
    asset: Optional[int] = None            # CollateralAsset pk
    movement_date: date
    direction: str                         # "POST" | "RETURN"
    amount: float
    currency: str
    settles_call: Optional[int] = None     # MarginCall pk
