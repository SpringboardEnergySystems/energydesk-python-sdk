
from energydeskapi.sdk.logging_utils import create_logstash_from_environment, LogstashConfig, setup_service_logging
import logging




if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    cf=LogstashConfig("192.168.1.72", 5000, "energydesk", "dev")
    setup_service_logging("heinz",enable_logstash_conf= cf)
    logger = logging.getLogger("heinz")
    logger.info("Hei på deg")