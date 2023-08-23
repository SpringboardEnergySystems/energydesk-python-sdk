import logging
from energydeskapi.sdk.datetime_utils import convert_datime_to_locstr
from dateutil import parser
import pandas as pd

logger = logging.getLogger(__name__)


def resolve_date_from_strutctime(iso_str, target_tz="Europe/Oslo"):
    dt = parser.isoparse(iso_str)
    loc = convert_datime_to_locstr(dt, target_tz)
    return loc[:10]

# Takes a REST JSON list and produces a dataframe with ticker, delivery information
def convert_productjson_dataframe(jsondata):
    data = []
    for p in jsondata['results']:
        ticker = p['commodity_definition']['product_code']
        instrument = p['commodity_definition']['instrument_type']['code']
        area = p['commodity_definition']['area']
        market = p['commodity_definition']['market']['description']
        dts_from = resolve_date_from_strutctime(p['commodity_definition']['delivery_from'])
        dts_until = resolve_date_from_strutctime(p['commodity_definition']['delivery_until'])
        tts_from = resolve_date_from_strutctime(p['traded_from'])
        tts_until = resolve_date_from_strutctime(p['traded_until'])
        data.append({'pk': p['pk'], 'ticker': ticker, 'instrument': instrument, 'market': market, 'area': area,
                     'traded_from': tts_from,
                     'traded_until': tts_until,
                     'delivery_from': dts_from,
                     'delivery_until': dts_until})
    df = pd.DataFrame(data=data)
    return df