from enum import Enum

class ProfileCategoryEnum(Enum):
    BASELOAD = 1
    PROFILE = 2
    ABSOLUTEPROFILE = 3  #Concrete periods rather than months, weekdays, hours

class MarketEnum(Enum):
    NORDIC_POWER = 1   # Key for the most commonly used markets
    GERMAN_POWER = 2
    CARBON_EMISSIONS = 3
    CURRENCY_MARKET = 4
    GOs_MARKET = 5

class DeliveryTypeEnum(Enum):
    FINANCIAL = 1
    PHYSICAL = 2

class CommodityTypeEnum(Enum):
    POWER = 1
    EUA = 2
    ELCERT = 3
    GAS = 4
    GOs = 5
    CURRENCY = 6

class InstrumentTypeEnum(Enum):
    FUT = 1
    FWD = 2
    SPOT = 3
    EPAD = 4
    EUROPT = 5
    ASIOPT = 6

class BlockSizeEnum(Enum):
    SPOT = 1
    DAY = 2
    WEEK = 3
    WEEKEND = 4
    MONTH = 5
    QUARTER = 6
    SEASON = 7
    YEAR = 8
