from enum import Enum

# A trading portfolio only holds Tradingbooks at the lowest levels
# A Hedging portfolio holds assets (e.g. with production forecasts) and trading books
# A Report portfolio is only used for owners reporting holding Physical and Account assets
class PortfolioTypeEnum(Enum):
    TRADING_PORTFOLIO = 1
    HEDGING_PORTFOLIO = 2
    REPORTING_PORTFOLIO = 3


class PeriodViewResolutionEnum(Enum):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    QUARTERLY = 4
    YEARLY = 5

class PeriodViewGroupingEnum(Enum):
    ALL = 0
    INSTRUMENT = 1
    AREA = 2
    TICKER = 3
