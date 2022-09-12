from enum import Enum


class ContractStatusEnum(Enum):
    REGISTERED = 1
    CONFIRMED = 2
    APPROVED = 3
    CANCELLED = 4


class ContractTypeEnum(Enum):
    FINANCIAL = 1
    PHYSICAL = 2

    @staticmethod
    def contract_type_code(x):
        return {
            1: 'FINANCIAL',
            2: 'PHYSICAL',
        }.get(x.value, '')

    @staticmethod
    def contract_type_description(x):
        return {
            1: 'Financial',
            2: 'Physical'
        }.get(x.value, '')

class InstrumentTypeEnum(Enum):
    SPOT = 1
    FORWARD = 2
    FUTURE = 3
    EUROPT = 4
    ASIOPT=5


    @staticmethod
    def instrument_type_code(x):
        return {
            1: 'SPOT',
            2: 'FORWARD',
            3: 'FUTURE',
            4: 'EUROPT',
            5: 'ASIOPT',
        }.get(x.value, '')

    @staticmethod
    def instrument_type_description(x):
        return {
            1: 'Spot',
            2: 'Forward',
            3: 'Future',
            4: 'European Option',
            5: 'Asian Option',
        }.get(x.value, '')

class CommodityTypeEnum(Enum):
    POWER = 1
    CO2 = 2
    ELCERT = 3
    GAS = 4
    GOs=5
    CURRENCY = 6

    @staticmethod
    def commodity_type_code(x):
        return {
            1: 'POWER',
            2: 'CO2',
            3: 'ELCERT',
            4: 'GAS',
            5: 'GOs',
            6: 'CURRENCY'
        }.get(x.value, '')

    @staticmethod
    def commodity_type_description(x):
        return {
            1: 'Power',
            2: 'CO2',
            3: 'Elcertificate',
            4: 'Gas',
            5: 'Guarantee of Origin',
            6: 'Currency'
        }.get(x.value, '')