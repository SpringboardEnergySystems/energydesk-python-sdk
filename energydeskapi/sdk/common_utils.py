import logging
from os.path import join, dirname
from dotenv import load_dotenv
import environ
from energydeskapi.sdk.datetime_utils import convert_loc_dateime_to_utcstr
from energydeskapi.sdk.api_connection import ApiConnection
logger = logging.getLogger(__name__)

def check_fix_date2str(dt):
    if isinstance(dt, str):
        return dt
    return convert_loc_dateime_to_utcstr(dt)

def load_env(current_dir):
    """ Loads environment file
    """
    logging.info("Loading environment from "+ str(current_dir))
    if current_dir is None:
        current_dir=dirname(__file__)
    dotenv_path = join(current_dir, '.env')
    load_dotenv(dotenv_path)


def init_api(current_dir=None):
    load_env(current_dir)
    env = environ.Env()
    if 'ENERGYDESK_TOKEN' in env:
        tok = env.str('ENERGYDESK_TOKEN')
    else:
        tok=None
    url= env.str('ENERGYDESK_URL')
    api_conn=ApiConnection(url)
    api_conn.set_token(tok, "Token")
    return api_conn

#For input from apps using eithe enum, int or str representing the same enumeration
def parse_enum_type(etype):
    if isinstance(etype, int) :
        return etype
    elif isinstance(etype, str) :
        return int(etype)
    else:
        return etype.value



# Given a REST entity url https://.../..././/object/x/  will return thee X value
def key_from_url(url):
    if url is None:
        return 0
    cols=url.split("/")
    try:
        return int(cols[-2:-1][0])
    except:
        return 0