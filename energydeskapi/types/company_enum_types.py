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
    UNDEFINED = 10

class UserRoleEnum(Enum):
    ADMIN = 1
    TRADER = 2
    RISKMANAGER =3
    MANAGER = 4
    STAKEHOLDER = 5
    BACKOFFICE = 6
    EXTERNAL_GUEST = 7
    ORIGINATOR = 8


class CounterpartTypeEnum(Enum):
    FEMA = 1
    INDUSTRIAL = 2
    FIXED =3
    GOO = 4
    NASDAQ = 5
    EEX = 6

def counterpart_type_description(x):
    return {
        CounterpartTypeEnum.FEMA: "Financial Energy Master Agreement",
        CounterpartTypeEnum.INDUSTRIAL: "Industry Contract",
        CounterpartTypeEnum.FIXED: "Fixed Price Contract",
        CounterpartTypeEnum.GOO: "Guarantee Of Origin Contract",
        CounterpartTypeEnum.NASDAQ: "Nasdaq Contract",
        CounterpartTypeEnum.EEX: "EEX Contract"
    }[x]