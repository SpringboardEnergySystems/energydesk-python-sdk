
import json
import logging
# Confluent Kafka is more tricky to install on Windows; hence using Apache version
from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from energydeskapi.events.event_subscriber import EventClient, EventSubscriber
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

    def publish(self,topic, msg, headers=[]):
        print("Sending", topic)
        result = self.producer.send(topic, msg)

        print(result)


    def connecnt_subscribers(self, topics, log_error=False, poll_interval=1800000):
        try:
            logger.info("Refreshing subscriber with max poll interval " + str(poll_interval))
            if poll_interval>1800000:
                self.consumer = KafkaConsumer(group_id=self.consumer_group,max_poll_interval_ms=poll_interval,session_timeout_ms=120000,request_timeout_ms=120001,connections_max_idle_ms=120002,
                                  bootstrap_servers=[self.kafka_host + ":" + str(self.kafka_port)],
                                  security_protocol=self.SECURITY_PROTOCOL,
                                  sasl_mechanism=self.SASL_MECHANISM,
                                  sasl_plain_username=self.kafka_user,
                                  sasl_plain_password=self.kafka_password,
                                  api_version=self.API_VERSION)
            else:
                self.consumer = KafkaConsumer(group_id=self.consumer_group,max_poll_interval_ms=poll_interval,
                                  bootstrap_servers=[self.kafka_host + ":" + str(self.kafka_port)],
                                  security_protocol=self.SECURITY_PROTOCOL,
                                  sasl_mechanism=self.SASL_MECHANISM,
                                  sasl_plain_username=self.kafka_user,
                                  sasl_plain_password=self.kafka_password,
                                  api_version=self.API_VERSION)
            logger.info("Subscribing Kafka to topics " + str(topics))
            self.consumer.subscribe(topics)
            return True
        except Exception as e:
            logger.error("Error refreshing connection " + str(e))
            return False

    def connect(self,subscriberlist,  consumer_group="default producer", log_error=True):
        self.consumer_group = consumer_group
        self.connect_producer()
        self.kafka_topics = []
        for es in subscriberlist:
            self.register_callback(es)
            self.kafka_topics.append(es.topic)  # Format is topic name and quality of service 1,2,3
        return self.connecnt_subscribers(self.kafka_topics)

    def start_listener(self,handler_pool_size=5, max_poll_interval_ms=1800000):
        try:
            pool = ThreadPoolExecutor(max_workers=handler_pool_size)
            logger.info("Checking subscribers")
            self.connecnt_subscribers(self.kafka_topics)
            while True:
                try:
                    logger.info("Checking consumer " + str(self.consumer))
                    for message in self.consumer:
                        content=None
                        msg_timestamp = datetime.fromtimestamp(message.timestamp / 1e3)
                        # if is_df:
                        #     txtmsg = str(message.value.decode('utf-8'))
                        #     payload = json.loads(txtmsg)
                        #     content = pd.read_json(payload)
                        # else:
                        content=str(message.value.decode('utf-8'))
                        logger.debug("Received content on " + message.topic)
                        self.handle_callback(message.topic, content)
                except Exception as e:
                    logger.warning("Error in subscriber " + str(e))
                    time.sleep(30)
                    self.connecnt_subscribers(self.kafka_topics)
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