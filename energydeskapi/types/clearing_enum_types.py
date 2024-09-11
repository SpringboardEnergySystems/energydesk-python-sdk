from enum import Enum

class ClearingHouse(Enum):
    NASDAQ = 1
    ABNAMRO = 2
    SEB = 3


    @staticmethod
    def clearing_house_code(x):
        return {
            1: 'NASDAQOMX',
            2: 'ABNAMRO',
            3: 'SEB'
        }.get(x.value, '')

    @staticmethod
    def clearing_house_description(x):
        return {
            1: 'Nasdaq OMX',
            2: 'ABN AMRO',
            3: 'SEB'
        }.get(x.value, '')

    @staticmethod
    def clearing_house_type_from_code(x):
        return {
            'NASDAQOMX': ClearingHouse.NASDAQ,
            'ABNAMRO': ClearingHouse.ABNAMRO,
            'SEB': ClearingHouse.SEB,
        }.get(x, 0)

    @staticmethod
    def clearing_house_type_from_name(x):
        return {
            'Nasdaq OMX': ClearingHouse.NASDAQ,
            'ABN AMRO': ClearingHouse.ABNAMRO,
            'SEB': ClearingHouse.SEB,
        }.get(x, 0)

class ClearingReportFormat(Enum):
    ORIGINAL = 1
    INTERNAL = 2

    @staticmethod
    def clearing_repformat_code(x):
        return {
            1: 'ORIGINAL',
            2: 'INTERNAL'
        }.get(x.value, '')

class ClearingReportTypeEnum(Enum):
    TRANSACTIONS = 1
    POSITIONS = 2
    ACCMVALUE = 3
    DELIVERY = 4
    FUTMTM = 5
    NONPROPMRGINTRA = 6
    COLLATVALUE = 7
    CASHOPTIMIZATION = 8
    ACCUMMVALUE = 9
    SPAN_PARAM_FILEHEADERLIST = 10
    SPAN_PARAM_RISKGROUPLIST = 11
    SPAN_PARAM_CONTRACTINFOLIST = 12
    SPAN_PARAM_RISKARRAYSLIST = 13
    SPAN_PARAM_CORRELATIONLIST = 14
    SPAN_PARAM_TIMESPREADLIST = 15
    SPAN_PARAM_CURRENCYCONVERSIONLIST = 16
    SPAN_PARAM_RNPDEFINITIONSLIST = 17
    SPAN_PARAM_RNPELEMENTSLIST = 18
    SPAN_PARAM_INTERCOMMODITYSPREADCREDITSLIST = 19
    SPAN_PARAM_DELIVERYCALENDARDATALIST = 20
    SPAN_PARAM_NONDELIVERYDATESLIST = 21
    SPAN_PARAM_TIMEPERIODLIST = 22
    SPAN_PARAM_TRAILERLIST = 23

    @staticmethod
    def clearing_report_type_code(x):
        return {
            1: 'TRANSACTIONS',
            2: 'POSITIONS',
            3: 'ACCMVALUE',
            4: 'DELIVERY',
            5: 'FUTMTM',
            6: 'NONPROPMRGINTRA',
            7: 'COLLATVALUE',
            8: 'CASHOPTIMIZATION',
            9: 'ACCUMMVALUE',
            10: 'SPAN_PARAM_FILEHEADERLIST',
            11: 'SPAN_PARAM_RISKGROUPLIST',
            12: 'SPAN_PARAM_CONTRACTINFOLIST',
            13: 'SPAN_PARAM_RISKARRAYSLIST',
            14: 'SPAN_PARAM_CORRELATIONLIST',
            15: 'SPAN_PARAM_TIMESPREADLIST',
            16: 'SPAN_PARAM_CURRENCYCONVERSIONLIST',
            17: 'SPAN_PARAM_RNPDEFINITIONSLIST',
            18: 'SPAN_PARAM_RNPELEMENTSLIST',
            19: 'SPAN_PARAM_INTERCOMMODITYSPREADCREDITSLIST',
            20: 'SPAN_PARAM_DELIVERYCALENDARDATALIST',
            21: 'SPAN_PARAM_NONDELIVERYDATESLIST',
            22: 'SPAN_PARAM_TIMEPERIODLIST',
            23: 'SPAN_PARAM_TRAILERLIST',
        }.get(x.value, '')


class ReconciliationStatusEnum(Enum):
    SUCCESS = 1
    ERROR = 2

    @staticmethod
    def reconciliation_status_code(x):
        return {
            1: 'SUCCESS',
            2: 'ERROR',
        }.get(x.value, '')


class ClearingReportQueryType(Enum):
    CLEARINGDATE = 1
    CLEARINGPERIOD = 2

    @staticmethod
    def clearing_report_query_code(x):
        return {
            1: 'CLEARINGDATE',
            2: 'CLEARINGPERIOD',
        }.get(x.value, '')
