from enum import Enum


class ContractStatusEnum(Enum):
    REGISTERED = 1
    CONFIRMED = 2
    APPROVED = 3
    CANCELLED = 4

class QuantityTypeEnum(Enum):
    EFFECT = 1
    VOLUME_TOTAL = 2
    VOLUME_YEARLY = 3
    CASH_AMOUNT = 4


class QuantityUnitEnum(Enum):
    KW = 1
    MW = 2
    GW = 3
    EUR = 4


class GosEnergySources(Enum):
    HYDRO = 1
    NORWEGIAN_HYDRO = 2