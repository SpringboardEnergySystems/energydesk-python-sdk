from decimal import *
from energydeskapi.sdk.money_utils import FormattedMoney, Money, CurrencyCode, gen_json_money, gen_money_from_json

def test_decimals():
    m=FormattedMoney(Decimal(3.7875), CurrencyCode.EUR)
    m3 = FormattedMoney("3.782500", CurrencyCode.EUR)
    print(m)
    print(m3)
    x=gen_json_money(m)
    print(x)
    m2=gen_money_from_json(x)
    m = Money(Decimal(1), CurrencyCode.EUR)
    print(m2)
    print(m+m2)

if __name__ == '__main__':
    test_decimals()