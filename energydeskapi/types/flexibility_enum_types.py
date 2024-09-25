from enum import Enum

class ReservesTypeEnums(Enum):
    mFRR = 1
    aFRR = 2
    FFR = 3
    FCR = 4

def reserves_type_description(x):
    return {
        ReservesTypeEnums.mFRR: "Manual Frequencey Containment Reserves",
        ReservesTypeEnums.aFRR: "Automatic Frequencey Containment Reserves",
        ReservesTypeEnums.FFR: "Fast Frequencey Reserves",
        ReservesTypeEnums.FCR: "Frequencey Containment Reserves"
    }[x]

class RegulatingDirectionEnums(Enum):
    DOWN=1
    UP=2
    SYMETRIC=3

def regulation_direction_description(x):
    return {
        RegulatingDirectionEnums.DOWN: "Down Regulation",
        RegulatingDirectionEnums.UP: "Up Regulation",
        RegulatingDirectionEnums.SYMETRIC: "Symetric",
    }[x]

class ReservesCategoryEnum(Enum):
    ACTIVATION=1
    CAPACITY=2

def reserves_category_description(x):
    return {
        ReservesCategoryEnum.ACTIVATION: "Activation",
        ReservesCategoryEnum.CAPACITY: "Capacity",
    }[x]


class RegulationTypeEnums(Enum):
    REGULATE_UP = 1
    REGULATE_DOWN = 2
    NO_REGULATION = 3

def regulation_type_description(x):
    return {
        RegulationTypeEnums.REGULATE_UP: "Regulate Up (consumption down)",
        RegulationTypeEnums.REGULATE_DOWN: "Regulate Down (consumption up)",
        RegulationTypeEnums.NO_REGULATION: "No Regulation"
    }[x]


class ExternalMarketTypeEnums(Enum):
    NODES = 1
    STATNETT_MFRR = 2


def external_flexmarkets_description(x):
    return {
        ExternalMarketTypeEnums.NODES: "NODES local flex market",
        ExternalMarketTypeEnums.STATNETT_MFRR: "Norwegian TSO mFRR"
    }[x]

class MaxUsageCriteria(Enum):
    FEWEST_REGULATIONS = 1
    LOWEST_ENERGY_COST = 2