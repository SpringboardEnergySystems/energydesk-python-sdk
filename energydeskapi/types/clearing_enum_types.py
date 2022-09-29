from enum import Enum


class ClearingReportTypeEnum(Enum):
    TRANSACTIONS = 1
    POSITIONS = 2
    ACCMVALUE = 3
    DELIVERY = 4
    FUTMTM = 5
    NONPROPMRGINTRA = 6
    COLLATVALUE = 7
    CASHOPTIMIZATION = 8
