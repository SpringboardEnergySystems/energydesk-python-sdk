from enum import Enum


class MarketEnum(Enum):
    NORDIC_POWER = 1   # Key for the most commonly used markets
    GERMAN_POWER = 2
    CURRENCY_MARKET = 3
    GOs_MARKET = 4

class CommodityTypeEnum(Enum):
    POWER = 1
    EUA = 2
    CO2 = 3
    ELCERT = 4
    GAS = 5
    GOs = 6
    CURRENCY = 7

class InstrumentTypeEnum(Enum):
    FUT = 1
    FWD = 2
    SPOT = 3
    EPAD = 4
    EUROPT = 5
    ASIOPT = 6