from enum import Enum

class AuditLogTypeEnums(Enum):
    CONTRACTS = 1


def auditlogtypes_description(x):
    return {
        AuditLogTypeEnums.CONTRACTS: "Contract Audit Trail",
    }[x]
