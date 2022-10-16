from enum import Enum

# A trading portfolio only holds Tradingbooks at the lowest levels
# A Hedging portfolio holds assets (e.g. with production forecasts) and trading books
# A Report portfolio is only used for owners reporting holding Physical and Account assets
class PortfolioTypeEnum(Enum):
    TRADING_PORTFOLIO = 1
    HEDGING_PORTFOLIO = 2
    REPORTING_PORTFOLIO = 3


class PeriodViewResolutionEnum(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    SEMI_MONTHLY = "SemiMonthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"

class PeriodViewGroupingEnum(Enum):
    NONE = "None"
    INSTRUMENT = "instrument"
    AREA = "area"
    TICKER = "ticker"
    ASSET = "asset"
