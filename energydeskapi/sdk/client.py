import logging
from energydeskapi.sdk.api_connection import ApiConnection
from energydeskapi.customers.customer_api import CustomerApi
from os.path import join, dirname
from dotenv import load_dotenv
import pytz, environ
from dateutil import parser
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

# Data retrieved from server are in UTC time ("GMT without daylight savings time")
# This function converts to local time
def convert_datetime_from_utc(utc_str, loczone="Europe/Oslo"):
    """ Converts datetime from UTC

    :param utc_str: string of UTC
    :type utc_str: str, required
    :param loczone: specified location
    :type loczone: str, required
    """
    timezone = pytz.timezone(loczone)
    utc_dt=parser.isoparse(str(utc_str))
    d_loc = utc_dt.astimezone(timezone)
    return d_loc

def load_env():
    """ Loads environment file

    """
    logging.info("Loading environment")
    dotenv_path = join(dirname(__file__), 'sample.env')
    load_dotenv(dotenv_path)

if __name__ == '__main__':
    load_env()
    env = environ.Env()
    tok = env.str('ENERGYDESK_TOKEN')
    url= env.str('ENERGYDESK_URL')
    api_conn=ApiConnection(url)
    api_conn.set_token(tok, "Token")

    #price=CurveApi.get_period_price(api_conn, "2023-01-01", "2023-04-01","NO1", "EUR")
    #print(price)
    user_profile=CustomerApi.get_user_profile(api_conn)
    print(user_profile)
    #AssetsApi.get_asset_types(api_conn)
    CustomerApi.get_companies(api_conn)
