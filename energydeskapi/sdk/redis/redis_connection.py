import redis
import logging
import environ
logger = logging.getLogger(__name__)

def connect_to_redis():
    env = environ.Env()
    try:
        red_host="localhost" if not "REDIS_HOST" in env else env.str("REDIS_HOST")
        redis_timeput = "1" if not "REDIS_TIMEOUT_SECONDS" in env else env.str("REDIS_TIMEOUT_SECONDS")
        red_port = "6379" if not "REDIS_PORT" in env else env.str("REDIS_PORT")
        red_db = "1" if not "REDIS_DB" in env else env.str("REDIS_DB")
        logger.info("Connecting to redis " + str(red_host) + ":" + str(red_port) + " db" + str(red_db))
        redis_connection = redis.StrictRedis(host=red_host, port=int(red_port), db=int(red_db),
                                             socket_connect_timeout=int(redis_timeput),
                             socket_timeout=int(redis_timeput))
        return redis_connection
    except Exception as e:
        logging.warning("Could not connect to REDIS  " + str(e))
    return None
