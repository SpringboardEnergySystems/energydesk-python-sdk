from enum import Enum


class ContractStatusEnum(Enum):
    REGISTERED = 1
    CONFIRMED = 2
    APPROVED = 3
    CANCELLED = 4




class GosEnergySources(Enum):
    HYDRO = 1
    NORWEGIAN_HYDRO = 2