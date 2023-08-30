from enum import Enum

# TO use codes without +/- Moodys is used for naming https://en.wikipedia.org/wiki/Credit_rating
class CreditRatingEnums(Enum):
    Aaa = "AAA"
    Aa1 = "AA+"
    Aa2 = "AA"
    Aa3 = "AA-"
    A1 = "A+"
    A2 = "A"
    A3 = "A-"
    Baa1 = "BBB+"
    Baa2 = "BBB"
    Baa3 = "BBB-"
    Ba1 = "BB+"
    Ba2 = "BB"
    Ba3 = "BB-"
    B1 = "B+"
    B2 = "B"
    B3 = "B-"
    Caa1 = "CCC+"
    Caa2 = "CCC"
    Caa3 = "CCC-"
    Ca = "CC"
    C = "C"

class FinancialStatementsEnum(Enum):
    ffo = "FFO"
    debt_adj = "Debt (adjusted)"
    debt_ebitda = "Debt/EBITDA"
    ffo_debt = "FFO/Debt"
    weighting = "Weighting"
    weighted_ebitda = "Weighted EBITDA"
    weighted_ffo = "Weighted FFO"
    weighted_debt = "Weighted Debt"
    weighted_debt_ebitda = "Weighted Debt/EBITDA"
    weighted_ffo_debt = "Weighted FFO/Debt"

class DiversificationEnums(Enum):
    NEUTRAL = 0
    MODERATE = 1
    SIGNIFICANT = 2

class FinancialPolicyEnums(Enum):
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1

class LiquidityEnums(Enum):
    ADEQUATE = 0
    STRONG = 1
    EXCEPTIONAL = 2

class ComparableRatingsEnums(Enum):
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1

class ManagmentGovernanceEnums(Enum):
    WEAK = -2
    FAIR = -1
    SATISFACTORY = 0
    STRONG = 1

class CapStructEnums(Enum):
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2

class GovernmentInfluenceEnums(Enum):
    LOW = 0
    MODERATE = 1
    MODERATELY_HIGH = 2
    HIGH = 3


class CompetitivePosEnums(Enum):
    STRONG = 1
    ADEQUATE = 2
    WEAK = 3
    POSITIVE = 4
    VERY_POSITIVE = 5

