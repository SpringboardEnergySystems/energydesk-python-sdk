from enum import Enum

class ProfileTypeEnum(Enum):
    BASELOAD = 1
    PROFILE = 2
    ABSOLUTEPROFILE = 3  #Not relative month,weekday, hours, but a list of concrete periods
    CONTRACTPROFILE = 4

class MarketEnum(Enum):
    NORDIC_POWER = 1   # Key for the most commonly used markets
    GERMAN_POWER = 2
    CARBON_EMISSIONS = 3
    CURRENCY_MARKET = 4
    GOs_MARKET = 5

class MarketPlaceEnum(Enum):
    NASDAQ_OMX = 1
    NORDPOOL_SPOT = 2
    EEX = 3


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
    GRID_CAPACITY = 7

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



def delivery_type_description(x):
    return {
        DeliveryTypeEnum.FINANCIAL: "Financial Delivery",
        DeliveryTypeEnum.PHYSICAL: "Physical Delivery",
    }[x]

def commodity_type_description(x):
    return {
        CommodityTypeEnum.POWER: "Power",
        CommodityTypeEnum.EUA: "EUA",
        CommodityTypeEnum.ELCERT: "Elcertificate",
        CommodityTypeEnum.GAS: "Gas",
        CommodityTypeEnum.GOs: "Guarantees of Origin",
        CommodityTypeEnum.CURRENCY: "Currency",
        CommodityTypeEnum.GRID_CAPACITY: "Grid Capacity",
    }[x]

def blocksize_description(x):
    return {
        BlockSizeEnum.SPOT: "Spot Product",
        BlockSizeEnum.DAY: "Day Product",
        BlockSizeEnum.WEEK: "Week Product",
        BlockSizeEnum.WEEKEND: "Weekend Product",
        BlockSizeEnum.MONTH: "Month Product",
        BlockSizeEnum.QUARTER: "Quarterly Product",
        BlockSizeEnum.SEASON: "Seasonal Product",
        BlockSizeEnum.YEAR: "Yearly Product"
    }[x]


def instrument_type_description(x):
    return {
        InstrumentTypeEnum.FUT: "Future",
        InstrumentTypeEnum.FWD: "Forward",
        InstrumentTypeEnum.SPOT: "Spot",
        InstrumentTypeEnum.EPAD: "EPAD",
        InstrumentTypeEnum.EUROPT: "European Option",
        InstrumentTypeEnum.ASIOPT: "Asian Option",
    }[x]

def profile_type_description(x):
    return {
        ProfileTypeEnum.BASELOAD: "Baseload",
        ProfileTypeEnum.PROFILE: "Profile",
        ProfileTypeEnum.ABSOLUTEPROFILE: "Varying Volume",
        ProfileTypeEnum.CONTRACTPROFILE: "Contract Profile",
    }[x]

def market_description(x):
    return {
        MarketEnum.NORDIC_POWER: "Nordic Power",
        MarketEnum.GERMAN_POWER: "German Power",
        MarketEnum.CARBON_EMISSIONS: "European Carbon Market",
        MarketEnum.CURRENCY_MARKET: "Currency Market",
        MarketEnum.GOs_MARKET: "European GoO Market",
    }[x]

def market_place_description(x):
    return {
        MarketPlaceEnum.NASDAQ_OMX: MarketPlaceEnum.NASDAQ_OMX.name,
        MarketPlaceEnum.NORDPOOL_SPOT: "Nord Pool Spot",
        MarketPlaceEnum.EEX: "EEX",
    }[x]