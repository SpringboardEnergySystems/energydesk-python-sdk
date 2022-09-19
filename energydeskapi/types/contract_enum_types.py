from enum import Enum


class ContractStatusEnum(Enum):
    REGISTERED = 1
    CONFIRMED = 2
    APPROVED = 3
    CANCELLED = 4


class ContractTypeEnum(Enum):
    FINANCIAL = 1
    PHYSICAL = 2
