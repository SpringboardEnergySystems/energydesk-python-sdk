import json
from dataclasses import dataclass
from datetime import date
from typing import Optional

import pendulum

from energydeskapi.types.market_enum_types import MarketPlaceEnum, MarketEnum

from energydeskapi.sdk.api_connection import ApiConnection

@dataclass(frozen=True)
class HolidayWithMarket:
    market_place: MarketPlaceEnum
    market: Optional[MarketEnum]
    holiday_from: date
    holiday_until: date
    description: str

def holiday_hook(json_dict):
    def convert_item(key: str, value: object):
        if key in ["holiday_from", "holiday_until"]:
            return pendulum.parse(value, exact=True)
        elif key in ["market_place"]:
            return MarketPlaceEnum(value)
        elif key in ["market"]:
            return MarketEnum(value)
        else:
            return value
    return {key: convert_item(key, value) for (key, value) in json_dict.items()}

class CalendarApi:
    @staticmethod
    def get_holidays_in_period(api_connection: ApiConnection, target_date: date, period_from: date, period_until: date, market_place: MarketPlaceEnum, market: Optional[MarketEnum]=None, additional_parameters: dict = {}):
        parameters_original: dict = {
            "target_date": target_date.isoformat(),
            "holiday_from__gte": period_from.isoformat(),
            "holiday_from__lt": period_until.isoformat(),
            "market_place_id": market_place.value
        }
        parameters = parameters_original | ({"market_id": market.value} if market is not None else {}) | additional_parameters
        json_res = api_connection.exec_get_url("/api/calendar/query_holidays/", parameters)
        return CalendarApi._holidays_from_json(json_res)

    @staticmethod
    def _holidays_from_json(js: str):
        dct_list = json.loads(js, object_hook=holiday_hook)
        return [HolidayWithMarket(**dct) for dct in dct_list]
