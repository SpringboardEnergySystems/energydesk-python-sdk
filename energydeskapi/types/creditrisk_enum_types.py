from enum import Enum

# TO use codes without +/- Moodys is used for naming https://en.wikipedia.org/wiki/Credit_rating
class CreditRatingEnums(Enum):
    Aaa = 1
    Aa1 = 2
    Aa2 = 3
    Aa3 = 4
    A1 = 5
    A2 = 6
    A3 = 7
    Baa1 = 8
    Baa2 = 9
    Baa3 = 10
    Ba1 = 11
    Ba2 = 12
    Ba3 =13
    B1 = 14
    B2 = 15
    B3 = 16
    Caa1 = 17
    Caa2 = 18
    Caa3 = 19
    Ca = 20
    C = 21

class RatingCategoryEnums(Enum):
    TIER1 = (7,1)
    TIER2 = (10, 8)
    TIER3 = (13,11)
    TIER4 = (16, 14)
    TIER5 = (21, 17)

def get_tier_range(rating_category_enum):
    return {
        'TIER1': (7,1),
        'TIER2': (10, 8),
        'TIER3': (13,11),
        'TIER4': (16, 14),
        'TIER5': (21, 17)
    }.get(rating_category_enum.name)

def get_tier_range_text(rating_category_enum):
    limit = get_tier_range(rating_category_enum)
    print("LIMIT", limit)
    vals = {
        1: 'AAA',
        2: 'AA+',
        3: 'AA',
        4: 'AA-',
        5: 'A+',
        6: 'A',
        7: 'A-',
        8: 'BBB+',
        9: 'BBB',
        10: 'BBB-',
        11: 'BB+',
        12: 'BB',
        13: 'BB-',
        14: 'B+',
        15: 'B',
        16: 'B-',
        17: 'CCC+',
        18: 'CCC',
        19: 'CCC-',
        20: 'CC',
        21: 'C',
    }
    return vals.get(limit[1]), vals.get(limit[0])

def get_credit_rating_text(credit_rating_enum):
    return {
        1: 'AAA',
        2: 'AA+',
        3: 'AA',
        4: 'AA-',
        5: 'A+',
        6: 'A',
        7: 'A-',
        8: 'BBB+',
        9: 'BBB',
        10: 'BBB-',
        11: 'BB+',
        12: 'BB',
        13: 'BB-',
        14: 'B+',
        15: 'B',
        16: 'B-',
        17: 'CCC+',
        18: 'CCC',
        19: 'CCC-',
        20: 'CC',
        21: 'C',
    }.get(credit_rating_enum.value, '')

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

