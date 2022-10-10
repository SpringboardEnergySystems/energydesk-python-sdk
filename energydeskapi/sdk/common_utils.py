import json
import logging
from os.path import join, dirname
from dotenv import load_dotenv
import pytz, environ
from energydeskapi.sdk.api_connection import ApiConnection
logger = logging.getLogger(__name__)

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
    tok = env.str('ENERGYDESK_TOKEN')
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
