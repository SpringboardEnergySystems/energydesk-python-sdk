
import json
import logging
import ssl

from energydeskapi.events.event_subscriber import EventClient, EventSubscriber
import paho.mqtt.client as mqtt
from energydeskapi.sdk.common_utils import init_api
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)


def on_message_callback(client, userdata, message):
    try:
        logger.info("Received MQTT message from client " + str(client))
        content_str = message.payload.decode("utf-8")
        content = json.loads(content_str)
        userdata.handle_callback(message.topic, content)
    except Exception as e:
        logger.error("Error occured "  + str(e))
        logger.error(str(content))

class MqttClient(EventClient):
    def __init__(self, mqtt_host, mqtt_port, username=None , password=None, certificates={}):
        super().__init__()
        self.mqtt_host=mqtt_host
        self.mqtt_port=mqtt_port
        self.username=username
        self.password=password
        self.ca_certificate=None if 'ca_certificate' not in certificates else certificates['ca_certificate']
        self.client_certificate=None if 'client_certificate' not in certificates else certificates['client_certificate']
        self.client_key=None if 'client_key' not in certificates else certificates['client_key']

    def connect(self,subscriberlist, client_name="client",  log_error=True):
        self.client=None
        def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
            logger.info("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
            #client.subscribe( topics)  # Subscribe to the topic “digitest/test1”, receive any messages published on it
            paho_topics=[]
            for es in subscriberlist:
                self.register_callback(es)
                paho_topics.append((es.topic,2))  #Format is topic name and quality of service 1,2,3
            if len(paho_topics)>0:
                self.client.subscribe(paho_topics)  #Only subscribe if topics given here. Some clients are *publish only*
        try:
            logger.info("Initializing MQTT")
            self.client = mqtt.Client(client_name, transport="websockets")  # create new instance
            self.client.on_message = on_message_callback  # attach function to callback
            self.client.on_connect = on_connect
            if self.username is not None:
                self.client.username_pw_set(self.username, self.password)
            self.client.user_data_set(self)
            logger.info("Connecting " + str(self.mqtt_host) + ":"  + str(self.mqtt_port))
            print(self.client_certificate)
            if self.client_certificate is not None:
                self.client.tls_set(ca_certs=self.ca_certificate, certfile=self.client_certificate,
                                    keyfile=self.client_key, tls_version=ssl.PROTOCOL_TLSv1_2)
                self.client.tls_insecure_set(True)
            self.client.connect(self.mqtt_host, port=int(self.mqtt_port))  # connect to broker
        except Exception as e:
            logger.error(str(e))
            return False
        return True

    def publish(self,topic, msg):
        result = self.client.publish(topic, msg, qos=0, retain=True)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            logger.info(f"Send `{msg}` to topic `{topic}`")
        else:
            logger.warning(f"Failed to send message to topic {topic}" + str(result))
    def start_listener(self):
        self.client.loop_start()  # start the loop
        #self.client.loop_forever()  # Blocking. Not ideal if you want to have main threead available

def on_my_callback(topic, data):
    print("GOT CALLBACK",topic, data)

import time, environ

if __name__ == '__main__':
    api_conn = init_api()
    env = environ.Env()
    mqtt_broker = env.str('MQTT_HOST')
    mqtt_port = env.str('MQTT_PORT')
    mqtt_usr = None if "MQTT_USERNAME" not in env else env.str("MQTT_USERNAME")
    mqtt_pwd = None if "MQTT_PASSWORD" not in env else env.str("MQTT_PASSWORD")
    ca_cert = None if "MQTT_CA_CERT" not in env else env.str('MQTT_CA_CERT')
    client_cert = None if "MQTT_CLIENT_CERT" not in env else env.str('MQTT_CLIENT_CERT')
    client_key = None if "MQTT_CLIENT_KEY" not in env else env.str('MQTT_CLIENT_KEY')
    mqtt_certs = {'ca_certificate': ca_cert, 'client_certificate': client_cert, 'client_key': client_key}
    mqttcli=MqttClient(mqtt_broker,mqtt_port,mqtt_usr,mqtt_pwd, mqtt_certs)
    es=EventSubscriber("/marketdata/nordicpower/#",on_my_callback)
    mqttcli.connect( [es], "Feed Listener")
    mqttcli.start_listener()
    print("Going into final loop")
    while 1==1:
        time.sleep(1)
