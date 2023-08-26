from enum import Enum

class BaselinesModelsEnums(Enum):
    WEEKDAYS_PROFILE = 1
    WEEKLY_PROFILE = 2
    MOVING_AVERAGE = 3
    PROPHET = 4
    CUSTOM_R = 5

def baseline_description(x):
    return {
        BaselinesModelsEnums.WEEKDAYS_PROFILE: "WeekDay Hourly Profile",
        BaselinesModelsEnums.WEEKLY_PROFILE: "Weekly Profile",
        BaselinesModelsEnums.MOVING_AVERAGE: "Moving Average",
        BaselinesModelsEnums.PROPHET: "Prophet (sklearn)",
        BaselinesModelsEnums.CUSTOM_R: "Custom R Script",
    }[x]
