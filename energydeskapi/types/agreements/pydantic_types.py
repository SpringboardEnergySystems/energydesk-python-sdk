"""
Typed wire payloads for energydesk.apps.agreements.

ElectionSheetLifted mirrors the lifted columns on ElectionSheet (everything
else stays in the `elections` JSON blob, deliberately untyped here for the
same reason Terms doesn't close over rule types - see
plans/customer_account_model.md's "The election sheet" section).

CreditProfile mirrors the wire shape of
agreements/trading-accounts/{pk}/credit/ (appserver
interfaces/serializers.py::CreditProfileSerializer, wrapping
services.CreditProfile) - a resolved, read-only snapshot over
creditrisk/counterparts. Never write this back.

MasterAgreementSummary is a light read-only projection for UIs that need to
show "which agreement is this contract under" without the full nested
embedded shape (ElectionSheet, CSA, etc).
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ElectionSheetLifted(BaseModel):
    model_config = ConfigDict(extra="allow")

    schema_version: str
    early_termination_automatic: bool = False
    material_reason_credit_event: bool = True
    cross_default_threshold_amount: Optional[float] = None
    cross_default_threshold_currency: Optional[str] = None
    tangible_net_worth_threshold: Optional[float] = None
    floating_price_fallback: Optional[str] = None
    vat_treatment: Optional[str] = None
    expert_determination: bool = False


class RiskLimits(BaseModel):
    model_config = ConfigDict(extra="allow")

    pfe: Optional[float] = None
    cash_amount: Optional[float] = None
    contract_tenor: Optional[float] = None
    contract_volume: Optional[float] = None


class CreditProfile(BaseModel):
    """Wire shape of GET agreements/trading-accounts/{pk}/credit/."""
    model_config = ConfigDict(extra="allow")

    as_of: datetime
    rating_code: Optional[str] = None
    rating_category_tier: Optional[int] = None
    risk_limits: Optional[RiskLimits] = None
    risk_limits_source: Optional[str] = None   # "COMPANY_OVERRIDE" | "CATEGORY_DEFAULT" | None
    allowed_counterpart_types: List[str] = []
    volume_limit_mwh: Optional[float] = None
    has_annual_accounts: bool = False


class MasterAgreementSummary(BaseModel):
    model_config = ConfigDict(extra="allow")

    pk: int
    reference: str
    title: str
    agreement_type: str          # AgreementTypeEnum code
    status: str                  # AgreementStatusEnum code
    account_reference: Optional[str] = None
    effective_date: date
    termination_date: Optional[date] = None
    is_external_record: bool = False
