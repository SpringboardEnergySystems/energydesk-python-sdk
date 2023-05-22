from enum import Enum


class SystemFeaturesEnum(Enum):
    ASSET_MANAGEMENT = 1
    USER_MANAGEMENT = 2
    RISK_MANAGEMENT = 3
    STANDARD_CONTRACTS = 4
    BILATERAL_FIXPRICE = 5
    CLEARING_MANAGEMENT = 6
    GOO_CONTRACTS = 7
    FX_HEDGING = 8

class SystemAccessTypeEnum(Enum):
    READ_ACCESS = 1
    WRITE_ACCESS = 2

