import logging
import random
import time
from dataclasses import asdict
import environ
import logging
import sys
from energydeskapi.events.mqtt_events_api import MqttClient
from energydeskapi.events.kafka_events_api import KafkaClient
from energydeskapi.events.event_subscriber import EventSubscriber
from energydeskapi.events.kafka_events_authenticated import KafkaClientAuthenticated

from energydeskapi.microservices.scheduledevents.connectors import connect_to_kafka, connect_to_mqtt
import environ
from energydeskapi.events.mqtt_events_api import MqttClient, MqttException


logger = logging.getLogger(__name__)
env = environ.Env()

class EventHandler:
    def __init__(self, id):
        self.id=id
        self.kafkacli = None
        self.subscribers=[]

    def connect(self, queues_callback):
        try:
            self.subscribers=[]
            for v in queues_callback:
                self.subscribers.append(EventSubscriber(v[0], v[1]))
            self.kafkacli=connect_to_kafka(self.id, self.subscribers)
        except Exception as e:
            logger.error("Error when reconnecting", e)
            return None

    def _disconnected(self):
        logger.info("Disconnected from Kafka")

    def _reconnect(self):
        try:
            logger.info("Reconnecting to Kafka in 1 second")
            time.sleep(1)
            self.kafkacli=connect_to_kafka(self.id, self.subscribers)
        except Exception as e:
            logger.error("Error when trying to reconnect", e)
            return None

    def _reconnect_when_connection_error(self, result):
        if result >= 3 and result <= 6:
            self._reconnect()

    def send_data(self, json, topic: str, data_description: str):
        if self.kafkacli is not None:
            try:
                result = self.kafkacli.publish(topic, json, quality_of_service=self.quality_of_service, publish_timeout=self.publish_timeout)
                if result != 0:
                    self._reconnect_when_connection_error(result)
                    raise Exception(f"Sending {data_description} to Kafka got result {result}")
            except MqttException as e:
                self._reconnect_when_connection_error(e.status)
                raise Exception(f"Sending {data_description} to Kafka got {e}")
        else:
            logger.error(f"Not connected to Kafka. Not possible to send {data_description}")
