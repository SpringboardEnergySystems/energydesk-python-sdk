
import json
import logging
import paho.mqtt.client as mqtt
from energydeskapi.sdk.common_utils import init_api
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

class MqttClient:
    def __init__(self, mqtt_host, mqtt_port, username=None , password=None):
        self.mqtt_host=mqtt_host
        self.mqtt_port=mqtt_port
        self.username=username
        self.password=password

    def connect(self, callback_function, topics, client_name="client",  log_error=True):
        def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
            logger.info("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
            #client.subscribe( topics)  # Subscribe to the topic “digitest/test1”, receive any messages published on it
            paho_topics=[]
            for t in topics:
                paho_topics.append((t,2))  #Format is topic name and quality of service 1,2,3
            if len(topics)>0:
                client.subscribe(paho_topics)  #Only subscribe if topics given here. Some clients are *publish only*
        try:
            logger.info("Initializing MQTT")
            self.client = mqtt.Client(client_name)  # create new instance
            if callback_function is not None:
                self.client.on_message = callback_function  # attach function to callback
            self.client.on_connect = on_connect
            if self.username is not None:
                self.client.username_pw_set(self.username, self.password)
            self.topics=topics
            logger.info("Connecting " + str(self.mqtt_host) + ":"  + str(self.mqtt_port))
            self.client.connect(self.mqtt_host, port=int(self.mqtt_port))  # connect to broker
        except Exception as e:
            logger.error(str(e))
            return False
        return True


    def start_listener(self):
        self.client.loop_start()  # start the loop
        # logger.info("Setting up MQTT listener on topic" + str(self.subscriber_topic))
        # self.client.subscribe(topic)
        # self.client.loop_forever()

def on_message_test_callback(client, userdata, message):
    try:
        logger.info("Received MQTT message from client " + str(client))
        content_str = message.payload.decode("utf-8")
        content = json.loads(content_str)
        logger.info(content_str)
    except Exception as e:
        logger.error("Error occured "  + str(e))
        logger.error(str(content))



import time, environ

if __name__ == '__main__':
    api_conn = init_api()
    env = environ.Env()
    mqtt_broker = env.str('ENERGYDESK_MQTT_BROKER')
    mqtt_port= env.str('ENERGYDESK_MQTT_PORT')
    mqtt_usr=None if "ENERGYDESK_MQTT_USERNAME" not in env else env.str("ENERGYDESK_MQTT_USERNAME")
    mqtt_pwd = None if "ENERGYDESK_MQTT_PASSWORD" not in env else env.str("ENERGYDESK_MQTT_PASSWORD")
    mqttcli=MqttClient(mqtt_broker,mqtt_port,mqtt_usr,mqtt_pwd)
    mqttcli.connect(on_message_test_callback, ["/marketdata/nordicpower/#"], "Feed Listener")
    mqttcli.start_listener()

    while 1==1:
        time.sleep(1)
