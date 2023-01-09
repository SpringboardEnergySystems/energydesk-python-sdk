from enum import Enum



class KafkaQueues(Enum):
    NORDICPOWER_PRICES = "marketdata.prices.nordicpower"
    PRODUCTVIEWS = "portfolioview.productview"

class MqttTopics(Enum):
    NORDICPOWER_PRICES = "/marketdata/nordicpower/#"
    PRODUCTVIEWS = "/portfolioview/productview"