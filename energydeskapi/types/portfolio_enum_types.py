from enum import Enum

# A trading portfolio only holds Tradingbooks at the lowest levels
# A Hedging portfolio holds assets (e.g. with production forecasts) and trading books
# A Report portfolio is only used for owners reporting holding Physical and Account assets
class PortfolioTypeEnum(Enum):
    TRADING_PORTFOLIO = 1
    HEDGING_PORTFOLIO = 2
    REPORTING_PORTFOLIO = 3


class PeriodViewGroupingEnum(Enum):
    COUNTERPART = "counterpart"
    INSTRUMENT = "instrument"
    AREA = "area"
    TICKER = "ticker"
    ASSET = "asset"
    TRADEID = "trade_id"


class ParametersEnum(Enum):
    netpos={"internal":"netpos", "formatting":"float", "display":"NetPos MW"}
    sellpos = {"internal": "sellpos","formatting":"float", "display": "SellPos MW"}
    buypos = {"internal": "buypos", "formatting":"float","display": "BuyPos MW"}
    netvol = {"internal": "netvol", "formatting":"float", "display": "Vol MWh"}
    buyvol = {"internal": "buyvol", "formatting":"float", "display": "Buy MWh"}
    sellvol = {"internal": "sellvol","formatting":"float",  "display": "Sell MWh"}

    avgcost = {"internal": "avgcost", "formatting":"float", "display": "Avg Cost"}
    avgcostbuy = {"internal": "avgcostbuy","formatting":"float",  "display": "Buy Cost"}
    avgcostsell = {"internal": "avgcostsell", "formatting":"float", "display": "Sell Cost"}
    market = {"internal": "market", "formatting":"str","display": "Market"}
    asset = {"internal": "asset", "formatting":"str", "display": "Underlying"}
    area = {"internal": "area", "formatting":"str", "display": "Area"}
    instrument = {"internal": "instrument", "formatting":"str", "display": "Instr"}
    delivery_from = {"internal": "delivery_from", "formatting":"date", "display": "DelivFrom"}
    delivery_until = {"internal": "delivery_until", "formatting":"date", "display": "DelivTo"}
    hours = {"internal": "hours", "formatting":"int", "display": "Hours"}
    contracts = {"internal": "contracts", "formatting":"int", "display": "# Contracts"}
    ticker={"internal": "ticker","formatting":"str",  "display": "Product"}
    price = {"internal": "price", "formatting": "float", "display": "Price"}
    unreal = {"internal": "unreal", "formatting": "float", "display": "Unrealized"}

