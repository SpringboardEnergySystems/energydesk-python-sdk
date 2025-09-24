from energydeskapi.sdk.common_utils import init_api
from energydeskapi.sdk.logging_utils import create_logstash_from_environment, LogstashConfig, setup_service_logging
import logging
import environ
logger = logging.getLogger(__name__)



if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    #env = environ.Env()
    api_conn_basic = init_api()
    cf=create_logstash_from_environment()
    setup_service_logging(__name__,enable_logstash_conf= cf)

    logger.info("Test output")
    logger.info("Enda en test")