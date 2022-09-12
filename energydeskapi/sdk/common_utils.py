import json
import logging
from os.path import join, dirname
from dotenv import load_dotenv
import pytz, environ
from energydeskapi.sdk.api_connection import ApiConnection
logger = logging.getLogger(__name__)

def load_env(current_dir=None):
    """ Loads environment file
    """
    logging.info("Loading environment")
    if current_dir is None:
        current_dir=dirname(__file__)
    dotenv_path = join(current_dir, '.env')
    load_dotenv(dotenv_path)


def init_api():
    load_env()
    env = environ.Env()
    tok = env.str('ENERGYDESK_TOKEN')
    url= env.str('ENERGYDESK_URL')
    api_conn=ApiConnection(url)
    api_conn.set_token(tok, "Token")
    return api_conn