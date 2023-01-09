from enum import Enum



class KafkaQueues(Enum):
    NORDICPOWER_PRICES = "marketdata.prices.nordicpower"


class MqttTopics(Enum):
    NORDICPOWER_PRICES = "/marketdata/nordicpower/#"