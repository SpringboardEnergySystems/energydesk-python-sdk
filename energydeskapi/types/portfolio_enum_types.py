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
    netpos={"internal":"netpos", "formatting":"float", "display":"NetPos MW"}
    sellpos = {"internal": "sellpos","formatting":"float", "display": "SellPos MW"}
    buypos = {"internal": "buypos", "formatting":"float","display": "BuyPos MW"}
    netvol = {"internal": "netvol", "formatting":"float", "display": "Vol MWh"}
    buyvol = {"internal": "buyvol", "formatting":"float", "display": "Buy MWh"}
    sellvol = {"internal": "sellvol","formatting":"float",  "display": "Sell MWh"}

    avgcost = {"internal": "avgcost", "formatting":"float", "display": "Avg Cost"}
    avgcostbuy = {"internal": "avgcostbuy","formatting":"float",  "display": "Sell Cost"}
    avgcostsell = {"internal": "avgcostsell", "formatting":"float", "display": "Buy Cost"}
    market = {"internal": "market", "formatting":"str","display": "Market"}
    asset = {"internal": "asset", "formatting":"str", "display": "Underlying"}
    area = {"internal": "area", "formatting":"str", "display": "Area"}
    instrument = {"internal": "instrument", "formatting":"str", "display": "Instr"}
    delivery_from = {"internal": "delivery_from", "formatting":"date", "display": "DelivFrom"}
    delivery_until = {"internal": "delivery_until", "formatting":"date", "display": "DelivTo"}
    hours = {"internal": "hours", "formatting":"int", "display": "Hours"}
    contracts = {"internal": "contracts", "formatting":"int", "display": "# Contracts"}
    ticker={"internal": "tcker","formatting":"str",  "display": "Product"}
    price = {"internal": "price", "formatting": "float", "display": "Price"}
    mtm = {"internal": "mtm", "formatting": "float", "display": "MtM"}

