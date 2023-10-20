
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
    def formatted_value(self, max_digits=5):
        strval=format_decimal(self.amount, decimal_places=max_digits, truncate=True)
        dec = max(strval.find("."), strval.find(","))
        if dec>=0:  # Do not strip 0 if no decimal
            strval = strval.rstrip('0')
            missing=2-(len(strval)-dec)
            if missing == 1: strval=strval+"0"
            if missing == 2: strval = strval + "00"
            return strval
        else:
            return strval + ",00"


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
            "amount": float(parse_decimal(mon.formatted_value())),  #Sent in Cents, Pence etc
            "currency": str(mon.currency.value)
    }
    return json

def gen_money_from_json(mon_json):
    print(parse_decimal(mon_json['amount']))
    nval=parse_decimal(mon_json['amount'])
    c=CurrencyCode._value2member_map_[mon_json['currency']]
    mny=Money(nval, c)
    return mny
