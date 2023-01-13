from enum import Enum
# test2


class KafkaQueues(Enum):
    NORDICPOWER_PRICES = "marketdata.prices.nordicpower"
    PRODUCTVIEWS = "portfolioview.productview"

class MqttTopics(Enum):
    NORDICPOWER_PRICES = "/marketdata/nordicpower/#"
    PRODUCTVIEWS = "/portfolioview/productview"