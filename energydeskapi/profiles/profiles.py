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

@dataclass
class GenericProfile:
    monthly_profile:  List[PeriodProfile]
    weekday_profile:  List[PeriodProfile]
    daily_profile:  List[PeriodProfile]
    def to_dict(self):
        return {'monthly_profile':{ obj.period:obj.factor for obj in self.monthly_profile},
                'weekday_profile':{ obj.period:obj.factor for obj in self.weekday_profile},
                'daily_profile':{ obj.period:obj.factor for obj in self.daily_profile}}

    @staticmethod
    def __from_individual_dict( dictionay):
        reslist=[]
        for key in dictionay.keys():
            reslist.append(PeriodProfile(key, dictionay[key]))
        return reslist

    @staticmethod
    def from_dict(dictionary):
        months=GenericProfile.__from_individual_dict(dictionary['monthly_profile'])
        weekdays = GenericProfile.__from_individual_dict(dictionary['weekday_profile'])
        daily = GenericProfile.__from_individual_dict(dictionary['daily_profile'])
        return GenericProfile(months, weekdays, daily)

if __name__ == '__main__':
    months=[PeriodProfile('January',90),PeriodProfile('February',70)]
    weekdays = [PeriodProfile('Monday', 3), PeriodProfile('Tuesday', 2)]
    daily = [PeriodProfile('0', 90), PeriodProfile('1', 70)]
    p=GenericProfile(months, weekdays, daily)
    print(p)
    print(asdict(p))
    d=p.to_dict()
    print(d)

    p2=GenericProfile.from_dict(d)
    print(p2)
    print(p2.to_dict())