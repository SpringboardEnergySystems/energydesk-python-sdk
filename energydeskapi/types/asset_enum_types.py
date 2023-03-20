from enum import Enum


class AssetTypeEnum(Enum):
    DR = 1
    BATTERY = 2
    GENERAL_PRODUCTION =3
    SOLAR = 4
    WIND = 5
    HYDRO = 6
    ACCOUNT = 7
    HEAT = 8
    GENERAL_CONSUMPTION = 9

class AssetForecastAdjustEnum(Enum):
    PERCENTAGE = 1
    EUROP_OPTION = 2
    ASIAN_OPTION = 3

