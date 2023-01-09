from enum import Enum
# test


class KafkaQueues(Enum):
    NORDICPOWER_PRICES = "marketdata.prices.nordicpower"


class MqttTopics(Enum):
    NORDICPOWER_PRICES = "/marketdata/nordicpower/#"