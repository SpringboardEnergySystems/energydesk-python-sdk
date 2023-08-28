from enum import Enum

class BaselinesModelsEnums(Enum):
    BUSINESSDAY_PROFILE = 1
    WEEK_RECURR_PROFILE = 2
    MOVING_AVERAGE = 3
    PROPHET = 4
    CUSTOM_R = 5

def baseline_description(x):
    return {
        BaselinesModelsEnums.BUSINESSDAY_PROFILE: "Business day Hourly Profile",
        BaselinesModelsEnums.WEEK_RECURR_PROFILE: "Weekly Recurring Profile",
        BaselinesModelsEnums.MOVING_AVERAGE: "Moving Average",
        BaselinesModelsEnums.PROPHET: "Prophet (sklearn)",
        BaselinesModelsEnums.CUSTOM_R: "Custom R Script",
    }[x]
