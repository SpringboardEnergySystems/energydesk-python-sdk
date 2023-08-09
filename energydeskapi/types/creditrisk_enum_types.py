from enum import Enum


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
    POSITIVE = 1
    VERY_POSITIVE = 2

