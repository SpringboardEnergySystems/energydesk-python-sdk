from enum import Enum

class ReportTypeEnum(Enum):
    PERIOD_VIEW = 1
    VAR = 2

def reporttype_description(x):
    return {
        ReportTypeEnum.PERIOD_VIEW: "Period View",
        ReportTypeEnum.VAR: "Value at Risk"
    }[x]


class ParameterUnits(Enum):
    MW = "MW"
    MWh = "MWh"
    NOK = "NOK"
    EUR = "EUR"
    kW = "kW"
    kWh = "kWh"