from enum import Enum


class CompanyTypeEnum(Enum):
    DOMESTIC = 1   # Mainly used for platform services in conjunction with demand side response
    INDUSTRIAL = 2
    UTILITY = 3
    GRID_OWNER = 4
    OPERATOR = 5
    BANK = 6
    TRADING_COMPANY = 7
    SERVICE_COMPANY = 8
    GENERAL_COMPANY = 9

# The company type is the main type of a company, but a company may have several roles (operator, bank) (asset owner, portfolio manager)
# Role is the most important property in terms of having appropriate access
class CompanyRoleEnum(Enum):
    DSO = 1
    FSP = 2
    BRP =3
    ASSET_OWNER = 4
    OPERATOR = 5
    BROKER = 6
    CLEARING_HOUSE = 7
    PORTFOLIO_MANAGER = 8
    BANK = 9

class UserRoleEnum(Enum):
    ADMIN = 1
    TRADER = 2
    RISKMANAGER =3
    STAKEHOLDER = 4