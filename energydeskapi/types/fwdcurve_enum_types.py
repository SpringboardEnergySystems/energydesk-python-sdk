from enum import Enum


class FwdCurveTypesEnum(Enum):
    PRICEIT = 1
    PRICEIT_ADJUSTED = 2
    FB_PROPHET = 3

class FwdCurveUsageEnum(Enum):
    GENERAL_PORTFOLIO_PRICING = 1
    BILATERAL_FIXED_PRICE = 2



