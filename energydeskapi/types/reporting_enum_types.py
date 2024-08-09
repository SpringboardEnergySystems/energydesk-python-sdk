from enum import Enum

class ReportTypeEnum(Enum):
    PRODUCT_VIEW = 1
    PERIOD_VIEW = 2
    CONTRACT_TIME_SERIES = 3
    VAR = 4

def reporttype_description(x):
    return {
        ReportTypeEnum.PRODUCT_VIEW: "Product View",
        ReportTypeEnum.PERIOD_VIEW: "Period View",
        ReportTypeEnum.CONTRACT_TIME_SERIES: "Contract Time Series",
        ReportTypeEnum.VAR: "Value at Risk"
    }[x]


class ParameterUnits(Enum):
    MW = "MW"
    MWh = "MWh"
    NOK = "NOK"
    EUR = "EUR"
    kW = "kW"
    kWh = "kWh"