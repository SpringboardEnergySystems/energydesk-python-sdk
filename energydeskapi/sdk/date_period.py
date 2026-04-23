from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class DatePeriod:
    from_date: date
    until_date: date
    def __str__(self):
        return f"DatePeriod{self.from_date.isoformat()},{self.until_date.isoformat()}"

@dataclass(frozen=True)
class DatetimePeriod:
    from_datetime: datetime
    until_datetime: datetime
    def __str__(self):
        return f"DatetimePeriod{self.from_datetime.isoformat()},{self.until_datetime.isoformat()}"


@dataclass(frozen=True)
class DatetimePeriodQuery:
    from_datetime: Optional[datetime]
    until_datetime: Optional[datetime]
    def __str__(self):
        return f"DatetimePeriodQuery{self.from_datetime.isoformat() if self.from_datetime is not None else ''},{self.until_datetime.isoformat() if self.until_datetime is not None else ''}"
