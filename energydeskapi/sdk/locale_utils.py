from energydeskapi.types.common_enum_types import CountryPrefEnum
#import locale
from babel.numbers import format_decimal as babel_format_decimal, decimal as babel_decimal

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
        return babel_format_decimal(dec, format='#,##0.' + dec_pattern + ';-#', locale=get_country_code(country_pref_enum), decimal_quantization=truncate)


if __name__ == '__main__':
    print(format_decimal(1000000.23533))#, CountryPrefEnum.NORWAY,decimal_places=3, truncate=True))
