from enum import Enum

class AuditLogTypeEnums(Enum):
    CONTRACTS = 1
    RISK_LIMITS = 2

def auditlogtypes_description(x):
    return {
        AuditLogTypeEnums.CONTRACTS: "Contract Audit Trail",
        AuditLogTypeEnums.RISK_LIMITS: "Risk Limit Audit Trail"
    }[x]
