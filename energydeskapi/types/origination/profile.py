"""
Typed wrapper for the `profile` JSON blob on DealVersion / ContractOffer.

See energydesk/apps/origination/README.md ("profile JSON"). Maps 1:1 onto
ContractPeriod at booking - `from`/`until` are period bounds
([from inclusive, until exclusive), matching the appserver's delivery-period
convention), `quantity_mwh` and `price` are the period's volume and price.
"""
from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class ProfilePeriod(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    from_: datetime = Field(alias="from")
    until: datetime
    quantity_mwh: float
    price: float


Profile = List[ProfilePeriod]
