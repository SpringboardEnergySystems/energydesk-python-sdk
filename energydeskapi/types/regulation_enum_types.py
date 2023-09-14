from enum import Enum

class RegulationEnums(Enum):
    REGULATE_UP = 1
    REGULATE_DOWN = 2


def regulation_description(x):
    return {
        RegulationEnums.REGULATE_UP: "Regulate Up (consumption down)",
        RegulationEnums.REGULATE_DOWN: "Regulate Down (consumption up)",
    }[x]
