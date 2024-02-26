from enum import Enum
# test2


class KafkaQueues(Enum):
    NORDICPOWER_PRICES = "marketdata.nordicpower.prices"
    NORDICPOWER_PRODUCTS = "marketdata.nordicpower.products"
    NORDICPOWER_OWNDEALS = "marketdata,nordicpower,owndeals"
    PRODUCTVIEWS = "portfolioview.productview"

class MqttTopics(Enum):
    NORDICPOWER_PRICES = "/marketdata/nordicpower/prices"
    NORDICPOWER_PRODUCTS = "/marketdata/nordicpower/products"
    NORDICPOWER_OWNDEALS = "/marketdata/nordicpower/owndeals"
    PRODUCTVIEWS = "/portfolioview/productview"