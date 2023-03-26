from dataclasses import dataclass, field
from typing import List
from datetime import date, datetime
from dataclasses import dataclass, asdict, field
from datetime import timezone, datetime, date
import json
from json import JSONEncoder
from dataclasses import dataclass
from energydeskapi.sdk.common_utils import dict_compare
#from dataclasses_json import dataclass_json
# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()
def date_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S+00:00")
        except:
            pass
    return json_dict
#@dataclass_json
@dataclass
class Expression:
    description: str
    adjustment_type: str  # AssetForecastAdjustEnum
    value: float
    denomination: str
    period_from: datetime
    period_until: datetime
    @property
    def __dict__(self):
        """
        get a python dictionary
        """
        return asdict(self)
    @property
    def json(self):
        """
        get the json formated string
        """
        return json.dumps(self.__dict__, cls=DateTimeEncoder)
    @staticmethod
    def from_json(elem):
        """
        get the json formated string
        """
        json_obj = json.loads(elem,object_hook=date_hook)
        mpobj = Expression(**json_obj)
        return mpobj


@dataclass
class Expressions:
    expressions:List
    @property
    def __dict__(self):
        """
        get a python dictionary
        """
        return asdict(self)
    @property
    def json(self):
        """
        get the json formated string
        """
        return json.dumps(self.__dict__, cls=DateTimeEncoder)
    @staticmethod
    def from_json(elem):
        """
        get the json formated string
        """
        json_obj = json.loads(elem,object_hook=date_hook)
        mpobj = Expressions(**json_obj)
        return mpobj