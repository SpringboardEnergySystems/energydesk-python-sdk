from enum import Enum


class AssetCategoryEnum(Enum):
    LONG_POSITION = 1
    SHORT_POSITION = 2
    BATTERY = 3
    BEHIND_THE_METER_LOAD = 4
    GROUPED_ASSET = 5

class AssetForecastAdjustDenomEnum(Enum):
    PERC = 1
    NOK = 2

class AssetForecastAdjustEnum(Enum):
    PERCENTAGE = 1
    EUROP_OPTION = 2
    ASIAN_OPTION = 3
    MONTHLY_PERC = 4

