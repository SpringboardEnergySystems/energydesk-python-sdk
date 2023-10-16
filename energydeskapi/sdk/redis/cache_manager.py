import logging
import environ
import redis
import pendulum
from datetime import timedelta
from datetime import datetime
import traceback
import sys
from energydeskapi.sdk.datetime_utils import conv_from_pendulum
from energydeskapi.sdk.redis.memory_cache import MemCache
from energydeskapi.sdk.redis.redis_connection import connect_to_redis
logger = logging.getLogger(__name__)

def current_date_pendulum(days_back=0, loczone="Europe/Oslo"):
    pendate=pendulum.today(tz=loczone)
    #print(pendate)
    pendate - pendate.subtract(days=days_back)
    #print(pendate)
    #pendate=pendate + timedelta(days=-days_back)
    return pendate

def current_date_localtime_dt(days_back=0, loczone="Europe/Oslo"):
    pd=current_date_pendulum(days_back, loczone)
    #print(conv_from_pendulum(pd, loczone))
    return conv_from_pendulum(pd, loczone)

def current_date_localtime(days_back=0, loczone="Europe/Oslo"):
    pd=current_date_pendulum(days_back, loczone)
    return str(pd)[:10]  #first 10
def get_cache():
    return connect_to_redis()

def get_memcache_value(cache_name, cache_key):
    mc=MemCache()
    if cache_name not in mc.mem_cache:
        print("Creating mem cache for " + cache_name)
        mc.mem_cache[cache_name]={}
    if cache_key not in mc.mem_cache[cache_name]:
        return None
    return mc.mem_cache[cache_name][cache_key]

def set_memcache_value(cache_name, cache_key, cache_value):
    mc=MemCache()
    if cache_name not in mc.mem_cache:
        print("Creating mem cache for " + cache_name)
        mc.mem_cache[cache_name]={}
    mc.mem_cache[cache_name][cache_key]=cache_value

def get_cache_value(cache_name, cache_key):
    r=get_cache()
    if r is not None:
        v=r.hget(cache_name, cache_key)
        return v
    else:
        return None

def remove_cache_value(cache_name, cache_key):
    r=get_cache()
    if r is not None:
        r.hdel(cache_name, cache_key)
        return True
    else:
        return False
def set_cache_value(cache_name, cache_key, cache_value):
    r=get_cache()
    if r is not None:
        r.hset(cache_name, cache_key, cache_value)


import logging
import pickle


def is_redis_disabled():
    env = environ.Env()
    b=False if "REDIS_HOST_DISABLED" not in env else env.bool("REDIS_HOST_DISABLED")
    return b

def cleanup_historical_datecache(cache_name, days_back=1):
    if is_redis_disabled():
        return None
    compressed_data=get_cache_value(cache_name, current_date_localtime(days_back))
    if compressed_data is None:
        return None
    uncompreessed = pickle.loads(compressed_data)
    return uncompreessed
def loadfrom_historical_datecache(cache_name, days_back=1):
    if is_redis_disabled():
        return None
    compressed_data=get_cache_value(cache_name, current_date_localtime(days_back))
    if compressed_data is None:
        return None
    uncompreessed = pickle.loads(compressed_data)
    return uncompreessed

def loadfrom_datecache(cache_name, date_resolution="%Y/W%V"):
    dt=current_date_localtime_dt()
    print(dt)
    dts=dt.strftime(date_resolution)
    print(dts)

    datekey =dts# current_date_localtime_dt().strftime(date_resolution)
    if is_redis_disabled():
        return get_memcache_value(cache_name, datekey)

    try:
        print("LOADING DATE CACHE", cache_name, datekey)
        compressed_data=get_cache_value(cache_name, datekey)
        print("VAL", compressed_data)
        if compressed_data is None:
            return None
        uncompreessed = pickle.loads(compressed_data)
        return uncompreessed
    except:
        execstr = traceback.format_exc()
        logger.error("Exception loading from REDIS " + str(execstr))
        return None

def saveto_datecache(cache_name,  v, date_resolution="%Y/W%V"):
    datekey = current_date_localtime_dt().strftime(date_resolution)
    if is_redis_disabled():
        set_memcache_value(cache_name, datekey, v)
        return True
    try:
        compressed_data = pickle.dumps(v, protocol=4)
        print("SAVING DATE CACHE", cache_name, datekey)
        set_cache_value(cache_name, datekey, compressed_data)
        return True
    except:
        execstr = traceback.format_exc()
        logger.error("Exception saving to REDIS " + str(execstr))
        return False
def loadfrom_staticcache(cache_name):
    if is_redis_disabled():
        return None
    compressed_data=get_cache_value(cache_name, "STATIC")
    if compressed_data is None:
        return None
    uncompreessed = pickle.loads(compressed_data)
    return uncompreessed
def saveto_staticcache(cache_name,  v):
    if is_redis_disabled():
        #Ignore saving
        return True
    compressed_data = pickle.dumps(v, protocol=4)
    set_cache_value(cache_name, "STATIC", compressed_data)

class ExpiryMapObj:
    def __init__(self, key, expiry, value):
        self.key=key
        self.expiry=expiry
        self.value=value
class ExpirationMap:
    def __init__(self):
        self.key_map={}

    def add_map(self, obj):
        self.key_map[obj.key]=obj

    def cleanup(self):
        for k in self.key_map.keys():
            obj=self.key_map[key]
            if obj.expiry<datetime.now():
                del self.key_map[key]


    def lookup(self, key):
        if key in self.key_map:
            obj=self.key_map[key]
            if obj.expiry>datetime.now():
                return obj
            else:
                del self.key_map[key]
                return None
        else:
            return None

def load_create_expiration_map(cache_name):
    compressed_data=get_cache_value("EXPIRATIONMAP", cache_name)
    if compressed_data is None:
        express_map=ExpirationMap()
        compressed_data = pickle.dumps(express_map, protocol=4)
        set_cache_value("EXPIRATIONMAP", cache_name, compressed_data)
        return express_map
    express_map = pickle.loads(compressed_data)
    return express_map
def loadfrom_expiration_cache(cache_name, cache_key):
    if is_redis_disabled():
        return None
    express_map=load_create_expiration_map(cache_name)
    gval=express_map.lookup(cache_key)
    compressed_data = pickle.dumps(express_map, protocol=4)
    set_cache_value("EXPIRATIONMAP", cache_name, compressed_data)
    return gval
def saveto_expiration_cache(cache_name, cache_key, expiraation_date, v):
    if is_redis_disabled():
        return True
    express_map = load_create_expiration_map(cache_name)
    expobj=ExpiryMapObj(cache_key,  expiraation_date, v)
    express_map.add_map(expobj)
    compressed_data = pickle.dumps(express_map, protocol=4)
    set_cache_value("EXPIRATIONMAP", cache_name,  compressed_data)

