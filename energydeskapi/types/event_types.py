from enum import Enum
# test2


class KafkaQueues(Enum):
    NORDICPOWER_PRICES = "marketdata.nordicpower.prices"
    NORDICPOWER_PRODUCTS = "marketdata.nordicpower.products"
    NORDICPOWER_OWNDEALS = "marketdata.nordicpower.owndeals"
    PRODUCTVIEWS = "portfolioview.productview"
    SCHEDULER_EVENTS = "system.schedulerevent"  # General Internal Event . Payload with more info
    FLEXIBILITY_SERVICES_EVENTS = "flexibility.service.events"  # General Internal Event . Payload with more info

class MqttTopics(Enum):
    NORDICPOWER_PRICES = "/marketdata/nordicpower/prices"
    NORDICPOWER_PRODUCTS = "/marketdata/nordicpower/products"
    NORDICPOWER_OWNDEALS = "/marketdata/nordicpower/owndeals"
    PRODUCTVIEWS = "/portfolioview/productview"