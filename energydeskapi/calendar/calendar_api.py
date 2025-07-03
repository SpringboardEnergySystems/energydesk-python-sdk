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

def date_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = pendulum.parse(value, exact=True)
        except:
            pass
    return json_dict

class CalendarApi:
    @staticmethod
    def get_holidays_in_period(api_connection: ApiConnection, target_date: date, period_from: date, period_until: date, market_place: MarketPlaceEnum, market: Optional[MarketEnum]=None):
        market_text = f"&market_id={market.value}" if market is not None else ""
        json_res = api_connection.exec_get_url(f"api/calendar/query_holidays/?target_date={target_date.isoformat()}&holiday_from__gte={period_from.isoformat()}&holiday_from__lt={period_until.isoformat()}&market_place_id={market_place.value}{market_text}")
        return CalendarApi._holidays_from_json(json_res)

    @staticmethod
    def _holidays_from_json(js: str):
        dct_list = json.loads(js, object_hook=date_hook)
        return [HolidayWithMarket(**dct) for dct in dct_list]
