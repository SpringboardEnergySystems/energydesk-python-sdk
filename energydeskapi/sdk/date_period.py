from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class DatePeriod:
    from_date: date
    until_date: date


@dataclass(frozen=True)
class DatetimePeriod:
    from_datetime: datetime
    until_datetime: datetime
