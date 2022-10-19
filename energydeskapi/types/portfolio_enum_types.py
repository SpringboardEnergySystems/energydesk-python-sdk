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


class ParametersEnum(Enum):
    netpos={"internal":"netpos", "display":"NetPos MW"}
    sellpos = {"internal": "sellpos", "display": "SellPos MW"}
    buypos = {"internal": "buypos", "display": "BuyPos MW"}
    netvol = {"internal": "netvol", "display": "Vol MWh"}
    buyvol = {"internal": "buyvol", "display": "Buy MWh"}
    sellvol = {"internal": "sellvol", "display": "Sell MWh"}

    avgcost = {"internal": "avgcost", "display": "Avg Cost"}
    avgcostbuy = {"internal": "avgcostbuy", "display": "Sell Cost"}
    avgcostsell = {"internal": "avgcostsell", "display": "Buy Cost"}
    market = {"internal": "market", "display": "Market"}
    asset = {"internal": "asset", "display": "Underlying"}
    area = {"internal": "area", "display": "Area"}
    instrument = {"internal": "instrument", "display": "Instr"}
    delivery_from = {"internal": "delivery_from", "display": "DelivFrom"}
    delivery_until = {"internal": "delivery_until", "display": "DelivTo"}
    hours = {"internal": "hours", "display": "Hours"}
    contracts = {"internal": "contracts", "display": "# Contracts"}
    ticker={"internal": "tcker", "display": "Product"}

