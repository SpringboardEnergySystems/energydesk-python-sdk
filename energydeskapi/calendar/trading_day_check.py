import logging

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, Any, Generator

from energydeskapi.calendar.calendar_api import HolidayWithMarket
from energydeskapi.types.market_enum_types import MarketPlaceEnum, MarketEnum

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class HolidayKey:
    market_place: MarketPlaceEnum
    market: Optional[MarketEnum]
    holiday_date: date

class TradingDayCheck:
    def __init__(self, holidays: list[HolidayWithMarket]):
        self._holidays_set = {holiday_day for holiday in holidays for holiday_day in TradingDayCheck._holiday_dates_in_period(holiday)}
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Holidays: {self._holidays_set}")

    def is_non_trading_day(self, target_date: date, market_place: MarketPlaceEnum, market: Optional[MarketEnum]) -> bool:
        return TradingDayCheck._is_weekend(target_date) or HolidayKey(market_place, market, target_date) in self._holidays_set  or HolidayKey(market_place, None, target_date) in self._holidays_set

    @staticmethod
    def _dates_in_period(period_from: date, period_until: date) -> Generator[date, Any, None]:
        dt = period_from
        while dt < period_until:
            yield dt
            dt += timedelta(days=1)

    @staticmethod
    def _holiday_dates_in_period(holiday: HolidayWithMarket) -> list[HolidayKey]:
        dates = TradingDayCheck._dates_in_period(holiday.holiday_from, holiday.holiday_until)
        return [HolidayKey(holiday.market_place, holiday.market, dt) for dt in dates]

    @staticmethod
    def _is_weekend(target_date: date) -> bool:
        return target_date.isoweekday() in [6, 7]






