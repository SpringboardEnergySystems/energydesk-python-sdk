from typing import List
import pytz
import dataclasses
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from json import JSONEncoder
from typing import List
import json
import pandas as pd
import pytz
import pendulum
from energydeskapi.sdk.datetime_utils import conv_from_pendulum
class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()

def date_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            pdt=pendulum.parse(value)
            dt=conv_from_pendulum(pdt)
            json_dict[key]=dt
            #json_dict[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S+00:00")
        except:
            pass
    return json_dict

@dataclass
class ContractProfilePeriod:
    period_from: datetime =  datetime(2022, 1, 1, 0, 0, 0,  tzinfo= pytz.timezone("Europe/Oslo"))
    period_until: datetime = datetime(2025, 1, 1, 0, 0, 0,  tzinfo= pytz.timezone("Europe/Oslo"))
    period_price: float = 0
    period_price_currency: str = "NOK"
    period_volume: float = 0
    period_effect: float = 0
    period_hours: float = 0


    def __dict__(self):
        d={
            'period_from':self.period_from if type(self.period_from)==str else self.period_from.isoformat(),
            'period_until': self.period_until if type(self.period_until)==str else self.period_until.isoformat()
        }
        if self.period_price is not None:
            d['period_price']=self.period_price
        if self.period_price_currency is not None:
            d['period_price_currency'] = self.period_price_currency
        if self.period_volume is not None:
            d['period_volume']=self.period_volume
        if self.period_effect is not None:
            d['period_effect'] = self.period_effect
        if self.period_hours is not None:
            d['period_hours'] = self.period_hours
        return d


    @property
    def json(self):
        return self.__dict__()
    @staticmethod
    def from_json(elem):
        """
        get the class from json
        """
        json_obj = json.loads(elem,object_hook=date_hook)
        mpobj = ContractProfilePeriod(**json_obj)
        #mpobj.period_from=datetime.strptime(mpobj.period_from, "%Y-%m-%dT%H:%M:%S+00:00")
        #mpobj.period_until = datetime.strptime(mpobj.period_until, "%Y-%m-%dT%H:%M:%S+00:00")
        if 'period_price' not in json_obj:
            mpobj.period_price=None
        if 'period_price_currency' not in json_obj:
            mpobj.period_price_currency=None
        if 'period_volume' not in json_obj:
            mpobj.period_volume=None
        if 'period_effect' not in json_obj:
            mpobj.period_effect=None
        if 'period_hours' not in json_obj:
            mpobj.period_hours=None
        return mpobj



@dataclass
class ContractProfile:
    profile_periods: List[ContractProfilePeriod]

    @property
    def json(self):
        """
        get the json formated string
        """
        return {'profile_periods':[p.json for p in self.profile_periods]}

    @staticmethod
    def from_json(elem):
        """
        get the json formated string
        """
        if type(elem)== str:
            json_obj = json.loads(elem,object_hook=date_hook)
        else:
            json_obj=elem
        parsed=[]
        for subperiod in json_obj['profile_periods']:
            cpp=ContractProfilePeriod.from_json(subperiod)
            parsed.append(cpp)
        mpobj = ContractProfile(parsed)
        return mpobj
    def generate_dataframe(self):  #Creates dictionaries pr profile
        dict_list=[]
        for t in self.trades:
            rec=dataclasses.asdict(t)#json.dumps(dataclasses.asdict(t),default=serializer_options)
            dict_list.append(rec)
        df = pd.DataFrame.from_dict(dict_list)
        return df
