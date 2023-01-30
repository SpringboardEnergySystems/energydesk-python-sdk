from dataclasses import dataclass, asdict, fields, is_dataclass
from typing import List
from types import GenericAlias
import json
from dataclasses import dataclass, field
from itertools import count
from datetime import datetime
from uuid import uuid4
import json
from datetime import timezone, datetime

@dataclass
class PeriodProfile:
    period: str
    factor: float
    def to_dict(self):
        return {self.period: self.factor}


@dataclass
class Profile:
    monthly_profile:  List[PeriodProfile]
    weekday_profile:  List[PeriodProfile]
    daily_profile:  List[PeriodProfile]
    def to_dict(self):
        return {'monthly_profile':{obj.to_dict() for obj in self.monthly_profile}}

if __name__ == '__main__':
    months=[PeriodProfile('January',90),PeriodProfile('February',70)]
    weekdays = [PeriodProfile('Monday', 3), PeriodProfile('Tuesday', 2)]
    daily = [PeriodProfile('0', 90), PeriodProfile('1', 70)]
    p=Profile(months, weekdays, daily)
    print(p)
    print(asdict(p))
    print(p.to_dict())