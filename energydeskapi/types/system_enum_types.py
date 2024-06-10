from enum import Enum


class SystemFeaturesEnum(Enum):
    CONTRACTS = 1
    CONTRACT_APPROVAL = 2
    ASSETS = 3
    ASSET_DATA = 4
    USERS = 5
    COMPANIES = 6
    TRADING_BOOKS = 7
    PORTFOLIOS = 8
    RISK_LIMITS = 9
    PORTFOLIO_TREE = 10
    PORTFOLIO_ACCESS = 11
    CREDIT_RISK_MATRIX = 12
    COMPANY_CREDIT_SCORE = 13
    VAR_CONFIG = 14
    FORWARD_CURVES = 15
    SCHEDULED_TASKS = 16

class SystemAccessTypeEnum(Enum):
    READ = 1
    CREATE = 2
    UPDATE = 3
    DELETE = 4
    REGISTER = 5
    CONFIRM = 6
    APPROVE = 7
    REOPEN = 8

def system_access_type_description(x):
    return {
        SystemAccessTypeEnum.READ: "Read",
        SystemAccessTypeEnum.CREATE: "Create",
        SystemAccessTypeEnum.UPDATE: "Update",
        SystemAccessTypeEnum.DELETE: "Delete",
        SystemAccessTypeEnum.REGISTER: "Register",
        SystemAccessTypeEnum.CONFIRM: "Confirm",
        SystemAccessTypeEnum.APPROVE: "Approve",
        SystemAccessTypeEnum.REOPEN: "Reopen"
    }[x]
def system_features_description(x):
    return {
        SystemFeaturesEnum.CONTRACTS: "Contract Management",
        SystemFeaturesEnum.CONTRACT_APPROVAL: "Contract Approval Process",
        SystemFeaturesEnum.ASSETS: "Assets",
        SystemFeaturesEnum.ASSET_DATA: "Asset Data (forecasts, meterdata)",
        SystemFeaturesEnum.USERS: "Users",
        SystemFeaturesEnum.COMPANIES: "Companies",
        SystemFeaturesEnum.TRADING_BOOKS: "Trading Books",
        SystemFeaturesEnum.PORTFOLIOS: "Portfolios",
        SystemFeaturesEnum.RISK_LIMITS: "Risk Limits",
        SystemFeaturesEnum.PORTFOLIO_TREE: "Portfolio Tree",
        SystemFeaturesEnum.PORTFOLIO_ACCESS: "Portfolio Access",
        SystemFeaturesEnum.CREDIT_RISK_MATRIX: "Credit Risk Matrix",
        SystemFeaturesEnum.COMPANY_CREDIT_SCORE: "Company Credit Score",
        SystemFeaturesEnum.VAR_CONFIG: "VaR Config",
        SystemFeaturesEnum.FORWARD_CURVES: "Forward Price Curves",
        SystemFeaturesEnum.SCHEDULED_TASKS: "Scheduled Tasks"
    }[x]
