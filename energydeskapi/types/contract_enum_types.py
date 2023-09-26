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