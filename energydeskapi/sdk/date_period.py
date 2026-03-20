from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class DatePeriod:
    from_date: date
    until_date: date


@dataclass(frozen=True)
class DatetimePeriod:
    from_datetime: datetime
    until_datetime: datetime


@dataclass(frozen=True)
class :
    from_datetime: Optional[datetime]
    until_datetime: Optional[datetime]
