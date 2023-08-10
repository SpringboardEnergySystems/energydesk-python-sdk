import logging
from os.path import join, dirname
from dotenv import load_dotenv
import environ
import jsonfield
import json
import re
from energydeskapi.sdk.datetime_utils import convert_loc_datetime_to_utcstr
from energydeskapi.sdk.api_connection import ApiConnection
logger = logging.getLogger(__name__)

def check_fix_date2str(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    return convert_loc_datetime_to_utcstr(dt)

def load_env(current_dir):
    """ Loads environment file
    """
    logging.info("Loading environment from "+ str(current_dir))
    if current_dir is None:
        current_dir=dirname(__file__)
    dotenv_path = join(current_dir, '.env')
    load_dotenv(dotenv_path)


def remove_alpha_num(indata):
    return re.sub("[^0-9]", "", str(indata))

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

def safe_prepare_json(json_input):  #If type is json string load as json
    if type(json_input)==str or type(json_input)==jsonfield.json.JSONString:
        json_input=json.loads(json_input)
    return json_input

def dict_compare(d1, d2, ignore_fields=[]):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    for el in ignore_fields:
        d1_keys.discard(el)
        d2_keys.discard(el)
    shared_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
    same = set(o for o in shared_keys if d1[o] == d2[o])
    return added, removed, modified, same