from enum import Enum




class PeriodResolutionEnum(Enum):
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    SEMI_MONTHLY = "SemiMonthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"

PERIOD_CHOICES=[el.value for el in PeriodResolutionEnum]