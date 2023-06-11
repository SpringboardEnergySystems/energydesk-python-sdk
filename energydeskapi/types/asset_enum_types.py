from enum import Enum


class AssetCategoryEnum(Enum):
    PRODUCTION = 1
    CONSUMPTION = 2
    BATTERY = 3
    BEHIND_THE_METER_LOAD = 4
    TRADING_ACCOUNT = 5
    GROUPED_ASSET = 6

class AssetForecastAdjustDenomEnum(Enum):
    PERC = 1
    NOK = 2

class AssetForecastAdjustEnum(Enum):
    PERCENTAGE = 1
    EUROP_OPTION = 2
    ASIAN_OPTION = 3
    MONTHLY_PERC = 4

