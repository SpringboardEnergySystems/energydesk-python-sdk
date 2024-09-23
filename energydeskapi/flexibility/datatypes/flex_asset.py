from datetime import datetime, date
import json
from enum import Enum
from json import JSONEncoder
from dataclasses import dataclass, asdict
from energydeskapi.flexibility.datatypes.json_encoder import DateTimeEncoder, date_hook

@dataclass(frozen=True)
class FlexAsset:
    pk: int
    asset_id: str
    description: str
    asset_category: str
    asset_type: str
    mpid: str
    sub_mpid: str
    availability: dict

    def __str__(self):
        attrs = vars(self)
        s="ProductPrice("  + (', '.join("%s: %s" % item for item in attrs.items())) + ")"
        return s

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
        mpobj = FlexAsset(**json_obj)
        return mpobj


@dataclass(frozen=True)
class RegulationEvent:
    asset_id: str
    extern_asset_id: str
    regulation_type: str
    regulation_start: datetime
    regulation_stop: datetime
    regulation_quantity: float


    def __str__(self):
        attrs = vars(self)
        s="RegulationEvent("  + (', '.join("%s: %s" % item for item in attrs.items())) + ")"
        return s

    @property
    def json(self):
        return json.dumps(self.__dict__, cls=DateTimeEncoder)
    @staticmethod
    def from_json(elem):
        json_obj = json.loads(elem,object_hook=date_hook)
        mpobj = RegulationEvent(**json_obj)
        return mpobj

