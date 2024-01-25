from enum import Enum

class RegulationTypeEnums(Enum):
    REGULATE_UP = 1
    REGULATE_DOWN = 2


def regulation_type_description(x):
    return {
        RegulationTypeEnums.REGULATE_UP: "Regulate Up (consumption down)",
        RegulationTypeEnums.REGULATE_DOWN: "Regulate Down (consumption up)"
    }[x]


class ExternalMarketTypeEnums(Enum):
    NODES = 1
    STATNETT_MFRR = 2


def external_flexmarkets_description(x):
    return {
        ExternalMarketTypeEnums.NODES: "NODES local flex market",
        ExternalMarketTypeEnums.STATNETT_MFRR: "Norwegian TSO mFRR"
    }[x]