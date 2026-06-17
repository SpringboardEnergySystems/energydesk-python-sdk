import json
import logging
import traceback
from datetime import datetime
from typing import Optional, Any

# Confluent Kafka is more tricky to install on Windows; hence using Apache version
from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.producer.future import FutureRecordMetadata

from energydeskapi.events.event_subscriber import EventClient, EventSubscriber
from energydeskapi.events.kafka_utils import decode_message
import time

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

# this uses Apache kafka for python
class KafkaClientAuthenticated(EventClient):
    def __init__(self, kafka_host: str, kafka_port: str, kafka_user: str, kafka_password: str,
                 security_protocol: str = "SASL_PLAINTEXT",
                 sasl_mechanism: str = "SCRAM-SHA-512",
                 api_version: tuple = (4, 1, 0)
                 ):
        super().__init__()
        self.kafka_host=kafka_host
        self.kafka_port=kafka_port
        self.kafka_user=kafka_user
        self.kafka_password=kafka_password
        self.security_protocol = security_protocol
        self.sasl_mechanism = sasl_mechanism
        self.api_version = api_version
        self.client = None


    def connect_producer(self, log_error: bool=True):
        try:
            server = self._build_server_address()
            self._log_connection("producer", server)
            self.producer = KafkaProducer(bootstrap_servers=[server],
                                          value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                                          security_protocol=self.security_protocol,
                                          sasl_mechanism=self.sasl_mechanism,
                                          sasl_plain_username=self.kafka_user,
                                          sasl_plain_password=self.kafka_password,
                                          api_version=self.api_version)
            return True
        except Exception as e:
            logger.error(f"Error refreshing connection {traceback.format_exc()}")
            return False

    def _build_server_address(self) -> str:
        return f"{self.kafka_host}:{self.kafka_port}"

    def _log_connection(self, connection_type: str, server: str) -> None:
        # , password {self.kafka_password}
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Connecting {connection_type} to {server} with protocol {self.security_protocol}, mechanism {self.sasl_mechanism}, user {self.kafka_user} and api version {self.api_version}")

    # if timeout_seconds is an integer it will wait for the acknowledge, otherwise it is meant as "fire and forget"
    def publish(self,topic: str, msg: Any, headers=[], timeout_seconds: Optional[int] = None) -> None:
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


    def connecnt_subscribers(self, topics: list[str], log_error=False, poll_interval=1800000) -> bool:
        try:
            logger.info("Refreshing subscriber with max poll interval " + str(poll_interval))
            server = self._build_server_address()
            self._log_connection("consumer", server)
            if poll_interval>1800000:
                self.consumer = KafkaConsumer(*topics, group_id=self.consumer_group,max_poll_interval_ms=poll_interval,session_timeout_ms=120000,request_timeout_ms=120001,connections_max_idle_ms=120002,
                                  bootstrap_servers=[server],
                                  security_protocol=self.security_protocol,
                                  sasl_mechanism=self.sasl_mechanism,
                                  sasl_plain_username=self.kafka_user,
                                  sasl_plain_password=self.kafka_password,
                                  api_version=self.api_version)
            else:
                self.consumer = KafkaConsumer(*topics, group_id=self.consumer_group,max_poll_interval_ms=poll_interval,
                                  bootstrap_servers=[server],
                                  security_protocol=self.security_protocol,
                                  sasl_mechanism=self.sasl_mechanism,
                                  sasl_plain_username=self.kafka_user,
                                  sasl_plain_password=self.kafka_password,
                                  api_version=self.api_version)
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

    def connect(self, subscriberlist: list[EventSubscriber],  consumer_group: str="default producer", log_error: bool=True) -> bool:
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


    def start_listener(self,handler_pool_size: int=5, max_poll_interval_ms: int=1800000, async_listening: bool=False) -> None:
        logger.info("********** In listener **********")
        self._stop_listener = False
        try:
            logger.info("Entering listener loop. Connecting subscribers.")
            self.connecnt_subscribers(self.kafka_topics, poll_interval=max_poll_interval_ms)
            if async_listening:
                logger.info("Reading messages from polling " + str(self.consumer))
            while not self._stop_listener:
                try:

                    if async_listening:
                        # Changed to non blocking making thread management more robust when shutting down gracefulley
                        records = self.consumer.poll(timeout_ms=10000)  # Non-blocking call with a timeout
                        for topic_partition, messages in records.items():
                            logger.info("Found partition " + str(topic_partition) + " with messages:")
                            for message in messages:
                                logger.info("Found message " + str(message))
                                msg_timestamp = datetime.fromtimestamp(message.timestamp / 1e3)
                                content, decoded_headers = decode_message(message)
                                logger.info(f"Received content on {message.topic} with headers {decoded_headers}")
                                self.handle_callback(message.topic, content, decoded_headers)
                    else:
                        logger.info("Reading messages from blocking " + str(self.consumer))
                        for message in self.consumer:
                            msg_timestamp = datetime.fromtimestamp(message.timestamp / 1e3)
                            content, decoded_headers = decode_message(message)
                            logger.debug(f"Received content on {message.topic} with headers {decoded_headers}")
                            self.handle_callback(message.topic, content, decoded_headers)
                except Exception as e:
                    logger.warning("Error in subscriber " + str(e))
                    time.sleep(30)
                    self.connecnt_subscribers(self.kafka_topics, poll_interval=max_poll_interval_ms)

            logger.warning("********** Exiting listener **********")
            self.consumer.unsubscribe()
            self.consumer.close()
        except Exception as e:
            logger.error(f"Error in subscriber {e} {traceback.print_exc()}")





# def on_test_callback(topic: str, data: Any):
#     print("Got callback from Kafka",topic, data)
#

# import time, environ
#
# if __name__ == '__main__':
#     api_conn = init_api()
#     env = environ.Env()
#     mqtt_broker = env.str('KAFKA_HOST')
#     mqtt_port= env.str('KAFKA_PORT')
#     mqttcli=KafkaClientAuthenticated(mqtt_broker,mqtt_port)
#     es=EventSubscriber("marketdata.nordicpower.nasdaqomx",on_test_callback)
#     mqttcli.connect( [es], "Feed Consumer")
#     mqttcli.start_listener()
#     while 1==1:
#         time.sleep(1)