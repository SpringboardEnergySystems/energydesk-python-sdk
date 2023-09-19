from enum import Enum

class RegulationTypeEnums(Enum):
    REGULATE_UP = 1
    REGULATE_DOWN = 2


def regulation_type_description(x):
    return {
        RegulationTypeEnums.REGULATE_UP: "Regulate Up (consumption down)",
        RegulationTypeEnums.REGULATE_DOWN: "Regulate Down (consumption up)"
    }[x]
