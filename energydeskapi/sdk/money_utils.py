
#from moneyed import Money
#from moneyed.l10n import format_money
from numbers import Number
from enum import Enum
from decimal import Decimal
from energydeskapi.sdk.locale_utils import format_decimal, parse_decimal
class CurrencyCode(Enum):
    NOK = "NOK"
    SEK = "SEK"
    DKK = "DKK"
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"

class Money:
    def __init__(self, amount, currency=CurrencyCode.EUR):
        self.amount = parse_decimal(str(amount))
        if type(currency)==str:
            self.currency = CurrencyCode._value2member_map_[currency]
        else:
            self.currency=currency
    def formatted_value(self, max_digits=9):
        tmp=format_decimal(self.amount, decimal_places=max_digits, truncate=True)
        #fmt='{:,.'+ str(max_digits)+ 'f}'
        #tmp=fmt.format(self.amount)
        tmp = tmp.rstrip('0')
        tmp= tmp if (tmp[-1:]!="." and tmp[-1:]!=",") else tmp + "0"  # If last 0 is removed, add
        return tmp
    def __repr__(self):   # Max digits, but strip trailing zeros
        return  self.formatted_value() + " " + self.currency.value
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
        if self.currency==CurrencyCode.EUR:
            return "€ " + self.formatted_value()
        elif self.currency==CurrencyCode.USD:
            return "$ " + self.formatted_value()
        elif self.currency==CurrencyCode.GBP:
            return "£ " + self.formatted_value()
        return  self.formatted_value() + " " + self.currency.value

def gen_json_money(mon):

    json =  {
            "amount": mon.formatted_value(),  #Sent in Cents, Pence etc
            "currency": str(mon.currency.value)
    }
    return json

def gen_money_from_json(mon_json):
    print(parse_decimal(mon_json['amount']))
    nval=parse_decimal(mon_json['amount'])
    c=CurrencyCode._value2member_map_[mon_json['currency']]
    mny=Money(nval, c)
    return mny
