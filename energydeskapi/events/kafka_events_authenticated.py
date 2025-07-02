
import json
import logging
from typing import Optional

# Confluent Kafka is more tricky to install on Windows; hence using Apache version
from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from kafka.producer.future import FutureRecordMetadata

from energydeskapi.events.event_subscriber import EventClient, EventSubscriber
from energydeskapi.events.kafka_utils import decode_message
from energydeskapi.sdk.common_utils import init_api
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

class KafkaClientAuthenticated(EventClient):
    SECURITY_PROTOCOL = "SASL_PLAINTEXT"
    SASL_MECHANISM = "PLAIN"
    API_VERSION = (3, 6, 0)

    def __init__(self, kafka_host, kafka_port, kafka_user, kafka_password):
        super().__init__()
        self.kafka_host=kafka_host
        self.kafka_port=kafka_port
        self.kafka_user=kafka_user
        self.kafka_password=kafka_password
        self.client = None


    def connect_producer(self, log_error=True):
        try:

            self.producer = KafkaProducer(bootstrap_servers=[self.kafka_host + ":" + str(self.kafka_port)],
                                          value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                                          security_protocol=self.SECURITY_PROTOCOL,
                                          sasl_mechanism=self.SASL_MECHANISM,
                                          sasl_plain_username=self.kafka_user,
                                          sasl_plain_password=self.kafka_password,
                                          api_version=self.API_VERSION)
            return True
        except Exception as e:
            logger.error("Error refreshing connection " + str(e))
            return False

    # if timeout_seconds is an integer it will wait for the acknowledge, otherwise it is meant as "fire and forget"
    def publish(self,topic, msg, headers=[], timeout_seconds: Optional[int] = None):
        logger.info(f"Sending to {topic}")
        future_result : FutureRecordMetadata = self.producer.send(topic, value=msg, headers=headers)
        if timeout_seconds is None:
            logger.info("Sent to kafka")
        else:
            try:
                result = future_result.get(timeout_seconds) # throws exception if something went wrong
                logger.info("Sent successfully to kafka")
                return result
            except Exception as ex:
                raise Exception(f"Sending {str(msg)[:300]} to kafka topic {topic} got {traceback.format_exc()}")


    def connecnt_subscribers(self, topics, log_error=False, poll_interval=1800000):
        try:
            logger.info("Refreshing subscriber with max poll interval " + str(poll_interval))
            if poll_interval>1800000:
                self.consumer = KafkaConsumer(*topics, group_id=self.consumer_group,max_poll_interval_ms=poll_interval,session_timeout_ms=120000,request_timeout_ms=120001,connections_max_idle_ms=120002,
                                  bootstrap_servers=[self.kafka_host + ":" + str(self.kafka_port)],
                                  security_protocol=self.SECURITY_PROTOCOL,
                                  sasl_mechanism=self.SASL_MECHANISM,
                                  sasl_plain_username=self.kafka_user,
                                  sasl_plain_password=self.kafka_password,
                                  api_version=self.API_VERSION)
            else:
                self.consumer = KafkaConsumer(*topics, group_id=self.consumer_group,max_poll_interval_ms=poll_interval,
                                  bootstrap_servers=[self.kafka_host + ":" + str(self.kafka_port)],
                                  security_protocol=self.SECURITY_PROTOCOL,
                                  sasl_mechanism=self.SASL_MECHANISM,
                                  sasl_plain_username=self.kafka_user,
                                  sasl_plain_password=self.kafka_password,
                                  api_version=self.API_VERSION)
            logger.info("Subscribing Kafka to topics " + str(topics))
            # NB KafkaConsumer does not work with consumer.subscribe([list]). This will only subscribe to the last item in the list
            # I found that a list can be based by converting the list to arguments *list in the constructor instead. This subscribes to all
            return True
        except Exception as e:
            logger.error("Error refreshing connection " + str(e))
            return False

    def disconnect(self):
        logger.info("Closing consumer and producer.")
        if self.consumer is not None:
            logger.info("Closing consumer and Unsubscribing from topics:")
            self._stop_listener=True
        if self.producer is not None:
            logger.info("Closing producer connection and waiting for it to close..")
            self.producer.close()

    def connect(self, subscriberlist,  consumer_group="default producer", log_error=True):
        self.consumer_group = consumer_group
        if self.connect_producer():
            if subscriberlist:
                self.kafka_topics = []
                for es in subscriberlist:
                    self.register_callback(es)
                    self.kafka_topics.append(es.topic)  # Format is topic name and quality of service 1,2,3
                return self.connecnt_subscribers(self.kafka_topics)
            else:
                return True
        else:
            return False


    def start_listener(self,handler_pool_size=5, max_poll_interval_ms=1800000):
        logger.info("********** In listener **********")
        self._stop_listener = False
        try:
            pool = ThreadPoolExecutor(max_workers=handler_pool_size)
            logger.info("Entering listener loop. Connecting subscribers.")
            self.connecnt_subscribers(self.kafka_topics)
            while not self._stop_listener:
                try:
                    # Changed to non blocking making thread management more robust when shutting down gracefulley
                    records = self.consumer.poll(timeout_ms=100)  # Non-blocking call with a timeout
                    for topic_partition, messages in records.items():
                        for message in messages:
                            msg_timestamp = datetime.fromtimestamp(message.timestamp / 1e3)
                            content, decoded_headers = decode_message(message)
                            logger.debug(f"Received content on {message.topic} with headers {decoded_headers}")
                            self.handle_callback(message.topic, content, decoded_headers)
                except Exception as e:
                    logger.warning("Error in subscriber " + str(e))
                    time.sleep(30)
                    self.connecnt_subscribers(self.kafka_topics,)
            logger.warning("********** Exiting listener **********")
            self.consumer.unsubscribe()
            self.consumer.close()
        except Exception as e:
            logger.error("Error in subscriber " + str(e))
            traceback.print_exc()




def on_test_callback(topic, data):
    print("Got callback from Kafka",topic, data)


import time, environ

if __name__ == '__main__':
    api_conn = init_api()
    env = environ.Env()
    mqtt_broker = env.str('KAFKA_HOST')
    mqtt_port= env.str('KAFKA_PORT')
    mqttcli=KafkaClientAuthenticated(mqtt_broker,mqtt_port)
    es=EventSubscriber("marketdata.nordicpower.nasdaqomx",on_test_callback)
    mqttcli.connect( [es], "Feed Consumer")
    mqttcli.start_listener()
    while 1==1:
        time.sleep(1)