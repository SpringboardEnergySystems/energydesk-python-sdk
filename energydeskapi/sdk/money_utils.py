
#from moneyed import Money
#from moneyed.l10n import format_money
from numbers import Number
from enum import Enum
from decimal import Decimal

class CurrencyCode(Enum):
    NOK = "NOK"
    SEK = "SEK"
    DKK = "DKK"
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"

class Money:
    def __init__(self, amount, currency_code=CurrencyCode.EUR):
        self.amount = Decimal(amount)
        self.currency_code=currency_code
    def formatted_value(self, max_digits=5):
        fmt='{:,.'+ str(max_digits)+ 'f}'
        tmp=fmt.format(self.amount)
        tmp = tmp.rstrip('0')
        return tmp
    def __repr__(self):   # Max digits, but strip trailing zeros
        return  self.formatted_value() + " " + self.currency_code.value
    def __str__(self):
        return self.__repr__()
    def __add__(self, other):
        if isinstance(other, Money):
            return Money(self.amount + other.amount)
        elif isinstance(other, Number):
            return Money(self.amount + other)
        else:
            return NotImplemented
    def __radd__(self, other):
        return self + other


class FormattedMoney(Money):
    def __str__(self):
        if self.currency_code==CurrencyCode.EUR:
            return "€ " + self.formatted_value()
        elif self.currency_code==CurrencyCode.USD:
            return "$ " + self.formatted_value()
        elif self.currency_code==CurrencyCode.GBP:
            return "£ " + self.formatted_value()
        return  self.formatted_value() + " " + self.currency_code.value

def gen_json_money(mon):
    json =  {
            "amount": mon.formatted_value(),  #Sent in Cents, Pence etc
            "currency": str(mon.currency_code.value)
    }
    return json

def gen_money_from_json(mon_json):
    print(mon_json)
    mny=Money(Decimal(mon_json['amount']), CurrencyCode._value2member_map_[mon_json['currency']])
    return mny
