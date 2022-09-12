
from moneyed import Money, NOK, EUR
from moneyed.l10n import format_money

class FormattedMoney(Money):
    def __str__(self):
        return format_money(self, locale='en_DE')

def gen_json_money(mon):
    json =  {
            "amount": int(float(mon.amount)*100),  #Sent in Cents, Pence etc
            "currency": str(mon.currency)
    }
    return json

def gen_money_from_json(mon_json):
    mny=FormattedMoney(float(mon_json['amount'])/100.0, mon_json['currency'])
    print(mny)
    return mny