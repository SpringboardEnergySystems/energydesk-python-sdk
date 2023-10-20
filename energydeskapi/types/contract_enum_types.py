from enum import Enum


class ContractStatusEnum(Enum):
    REGISTERED = 1
    CONFIRMED = 2
    APPROVED = 3
    CANCELLED = 4

class QuantityTypeEnum(Enum):
    EFFECT = 1
    VOLUME = 2
    VOLUME_YEARLY = 3
    CASH_AMOUNT = 4
    CERTIFICATE = 5
    PERCENTAGE = 6


class QuantityUnitEnum(Enum):
    KW = 1
    MW = 2
    GW = 3
    EUR = 4
    LOTS = 5
    DECIMALS = 6

class GosTechnologyEnum(Enum):
    HYDRO = 1
    WIND = 2
    SOLAR = 3

class GosEnergySources(Enum):
    HYDRO = 1
    NORWEGIAN_HYDRO = 2

class ContractTypeEnum(Enum):
    NASDAQ = 1
    EEX = 2
    BILAT_FIXPRICE = 3
    GOO = 4
    PROFILE = 5
    CAPACITY = 6



def quantity_type_description(x):
    return {
        QuantityTypeEnum.EFFECT: "Effect",
        QuantityTypeEnum.VOLUME: "Volume",
        QuantityTypeEnum.VOLUME_YEARLY: "Volume per year",
        QuantityTypeEnum.CASH_AMOUNT: "Cash Amount",
        QuantityTypeEnum.CERTIFICATE: "Certificates",
        QuantityTypeEnum.PERCENTAGE: "Percentage"
    }[x]

def quantity_unit_description(x):
    return {
        QuantityUnitEnum.KW: "Kilowatt",
        QuantityUnitEnum.MW: "Megawatt",
        QuantityUnitEnum.GW: "Gigawatt",
        QuantityUnitEnum.EUR: "EUR amount",
        QuantityUnitEnum.LOTS: "Lots",
        QuantityUnitEnum.DECIMALS: "Decimals"
    }[x]

def go_technology_description(x):
    return {
        GosTechnologyEnum.HYDRO: "Hydro power",
        GosTechnologyEnum.WIND: "Wind power",
        GosTechnologyEnum.SOLAR: "Solar power",
    }[x]

def contract_type_description(x):
    return {
        ContractTypeEnum.NASDAQ: "Nasdaq OMX",
        ContractTypeEnum.EEX: "EEX",
        ContractTypeEnum.BILAT_FIXPRICE: "Bilateral Fixed Price",
        ContractTypeEnum.GOO: "Guarantee of Origin",
        ContractTypeEnum.PROFILE: "Varying Periodic Profile",
        ContractTypeEnum.CAPACITY: "Capacity Contract"
    }[x]


def contract_status_description(x):
    return {
        ContractStatusEnum.REGISTERED: "Registered",
        ContractStatusEnum.CONFIRMED: "Confirmed",
        ContractStatusEnum.APPROVED: "Approved",
        ContractStatusEnum.CANCELLED: "Cancelled",
    }[x]