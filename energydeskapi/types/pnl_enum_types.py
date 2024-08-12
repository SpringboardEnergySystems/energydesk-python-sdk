from enum import Enum

class PnlPeriodEnums(Enum):
    DAY = 1,
    MONTH = 2,
    YEAR = 3


def get_pnl_param_name(e:PnlPeriodEnums):
    return {
        PnlPeriodEnums.DAY: "pnlday",
        PnlPeriodEnums.MONTH: "pnlmonth",
        PnlPeriodEnums.YEAR: "pnlyear",
    }[e]
