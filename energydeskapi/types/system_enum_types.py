from enum import Enum


class SystemFeaturesEnum(Enum):
    ASSET_MANAGEMENT = 1
    RISK_MANAGEMENT = 2
    STANDARD_CONTRACTS = 3
    BILATERAL_FIXPRICE = 4
    CLEARING_MANAGEMENT = 5
    GOO_CONTRACTS = 6
    FX_HEDGING = 7
    YIELD_CURVES = 8

class SystemAccessTypeEnum(Enum):
    READ = 1
    CREATE = 2
    UPDATE = 3
    DELETE = 4

