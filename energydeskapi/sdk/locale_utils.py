from energydeskapi.types.common_enum_types import CountryPrefEnum
#import locale
import pytz
from datetime import datetime
from dateutil import parser
import pendulum
from babel.numbers import parse_decimal as babel_parse_decimal,format_decimal as babel_format_decimal, decimal as babel_decimal
from babel.dates import format_datetime as babel_format_datetime, format_date as babel_format_date
def get_country_code(country_pref_enum=CountryPrefEnum.NORWAY):
    if country_pref_enum==CountryPrefEnum.NORWAY:
        return "nb_NO.utf-8"
    elif country_pref_enum==CountryPrefEnum.SWEDEN:
        return "sv_SE.utf-8"
    elif country_pref_enum==CountryPrefEnum.UK:
        return "en_GB.utf-8"
    elif country_pref_enum==CountryPrefEnum.US:
        return "en_US.utf-8"
    elif country_pref_enum==CountryPrefEnum.GERMANY:
        return "de_DE.utf-8"
    return "nb_NO.utf-8"  #Default

def format_decimal(dec, country_pref_enum=CountryPrefEnum.NORWAY, decimal_places=2, truncate=True):
    dec_pattern="".join(["0" for l in range(decimal_places)])  #Number of minimum decials
    with babel_decimal.localcontext(babel_decimal.Context(rounding=babel_decimal.ROUND_HALF_UP)):
        strdec= babel_format_decimal(dec, format='#,##0.' + dec_pattern + ';-#', locale=get_country_code(country_pref_enum), decimal_quantization=truncate)
        strdec = strdec.rstrip('0')
        strdec= strdec if (strdec[-1:]!="." and strdec[-1:]!=",") else strdec  # If last 0 is removed, add
        return strdec
def parse_decimal(dec_str, country_pref_enum=CountryPrefEnum.NORWAY):
    if type(dec_str) != str:
        return dec_str
    return babel_parse_decimal(dec_str,locale=get_country_code(country_pref_enum))

def format_datetime_from_dt(dt, format="yyyy.MM.dd  HH:mm:ss zzz",tzinfo=pytz.timezone('Europe/Oslo'),country_pref_enum=CountryPrefEnum.NORWAY):
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt=tzinfo.localize(dt)
    else:
        dt=dt.astimezone(tzinfo)
    return babel_format_datetime(dt, format=format, tzinfo=tzinfo, locale=get_country_code(country_pref_enum))

def format_datetime_from_iso(dts, format="yyyy.MM.dd  HH:mm:ss zzz",tzinfo=pytz.timezone('Europe/Oslo'), country_pref_enum=CountryPrefEnum.NORWAY):
    dt=parser.isoparse(dts)
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        print("Localizing")
        dt=tzinfo.localize(dt)
    else:
        print("Already localized")
        dt=dt.astimezone(tzinfo)
    return babel_format_datetime(dt, format=format,tzinfo=tzinfo, locale=get_country_code(country_pref_enum))
# Usage
#     df_trades['quantity']=df_trades.apply(format_pandas_decimalcol,colname = "quantity", country_pref_enum=CountryPrefEnum.NORWAY, axis=1)
def format_pandas_decimalcol(row, colname, country_pref_enum=CountryPrefEnum.NORWAY, decimal_places=2, truncate=True):
    return format_decimal(row[colname],country_pref_enum,decimal_places, truncate)

def format_pandas_datetimecol_from_iso(row, colname,format="yyyy.MM.dd  HH:mm:ss zzz", tzinfo=pytz.timezone('Europe/Oslo'), country_pref_enum=CountryPrefEnum.NORWAY):
    return format_datetime_from_iso(row[colname],format=format, tzinfo=tzinfo, country_pref_enum=country_pref_enum)

import pendulum
if __name__ == '__main__':
    print(format_decimal(1000000.23533))#, CountryPrefEnum.NORWAY,decimal_places=3, truncate=True))
    print(format_datetime_from_dt(datetime.now()))
    print(format_datetime_from_iso("2023-10-01"))
    print(format_datetime_from_iso("2023-10-01T01:00:00+02"))