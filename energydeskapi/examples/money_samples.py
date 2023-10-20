from decimal import *
from energydeskapi.sdk.money_utils import FormattedMoney, Money, CurrencyCode, gen_json_money, gen_money_from_json
from energydeskapi.sdk.locale_utils import format_decimal
def test_decimals():
    m=FormattedMoney(Decimal(30.0), CurrencyCode.EUR)
    m3 = FormattedMoney("3.782500", CurrencyCode.EUR)
    print(m)
    print(m3)
    x=gen_json_money(m3)
    print(x)
    m2=gen_money_from_json(x)
    m = Money(Decimal(1), CurrencyCode.EUR)
    print(m2)
    print(m+m2)
    print(format_decimal("90,0", truncate=False))

if __name__ == '__main__':
    test_decimals()