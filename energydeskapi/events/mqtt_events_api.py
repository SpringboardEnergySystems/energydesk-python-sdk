
import json
import logging
import ssl
from dataclasses import dataclass
from typing import Callable, Optional

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
        logger.debug("Received MQTT message from client " + str(client))
        content_str = message.payload.decode("utf-8")
        content = json.loads(content_str)
        # In parent class loops through subscriber handlers
        userdata.handle_callback(message.topic, content)
    except Exception as e:
        logger.error("Error occured "  + str(e))
        logger.error(str(content))

def on_disconnect(client, userdata, rc):
    logging.info("disconnecting reason  "  +str(rc))
    client.connected_flag=False
    client.disconnect_flag=True
    userdata.handle_disconnect()


class MqttException(Exception):
    def __init__(self, message, status=None):
        self.message = message
        self.status = status # you could add more args
    def __str__(self):
        return str(self.message)

class MqttSubscriber(EventSubscriber):
    def __init__(self, topic: str, callback_function: Callable[[str, str, list[tuple[str, any]]], None], qos: int=0):
        super(MqttSubscriber, self).__init__(topic, callback_function)
        self.qos = qos


class MqttClient(EventClient):
    def __init__(self, mqtt_host: str, mqtt_port: int,
                 username: str=None , password: str=None,
                 certificates: dict[str, any]= {}, force_transport: Optional[str] =None, use_tls: bool=False):
        super().__init__()
        self.connected=False
        self.mqtt_host=mqtt_host
        self.mqtt_port=mqtt_port
        self.username=username
        self.password=password
        self.ca_certificate = None if 'ca_certificate' not in certificates else certificates['ca_certificate']
        self.client_certificate = None if 'client_certificate' not in certificates else certificates['client_certificate']
        self.client_key = None if 'client_key' not in certificates else certificates['client_key']
        self.disconnect_callbacks = []
        #force_transport either tcp or websockets
        self.force_transport = force_transport
        self.use_tls = use_tls

    def disconnect(self):
        logger.info("Disconnecting MQTT") # TO be implemented

    def connect(self, subscriberlist: list[MqttSubscriber], client_name: str="client",  log_error=True):
        self.client=None

        def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
            #print("INSIDE ON CONNECT")
            logger.info("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
            #client.subscribe( topics)  # Subscribe to the topic “digitest/test1”, receive any messages published on it

            for es in subscriberlist:
                self.register_callback(es)
            if len(subscriberlist)>0:
                paho_topics = [(es.topic, es.qos) for es in subscriberlist]
                self.client.subscribe(paho_topics)  #Only subscribe if topics given here. Some clients are *publish only*
            #self.start_listener()
        try:
            logger.info("Initializing MQTT")
            if not self.force_transport is None:
                self.client = mqtt.Client(client_name, transport=self.force_transport)  # create new instance
                logger.info("Using MQTT transport "+self.force_transport)
            elif self.mqtt_port == "8080":
                self.client = mqtt.Client(client_name, transport="websockets")  # create new instance
                logger.info("Using MQTT transport Websockets")
            else:
                self.client = mqtt.Client(client_name)  # create new instance
                logger.info("Using MQTT transport Mqtt")
            self.client.on_message = on_message_callback  # attach function to callback
            self.client.on_connect = on_connect
            self.client.on_disconnect=on_disconnect
            if self.username is not None:
                logger.info(f"Setting userpass {self.username} {self.password}")
                self.client.username_pw_set(self.username, self.password)
            self.client.user_data_set(self)
            logger.info(f"Connecting {self.mqtt_host}:{self.mqtt_port}")
            #print(self.client_certificate)
            if self.use_tls is True:
                logger.info("Use TLS")
                if self.ca_certificate is None:
                    logger.info("Setting no CA certificate")
                    self.client.tls_set(certfile=self.client_certificate,
                                        keyfile=self.client_key, tls_version=ssl.PROTOCOL_TLSv1_2)
                else:
                    logger.info("Setting CA certificate")
                    self.client.tls_set(ca_certs=self.ca_certificate, certfile=self.client_certificate,
                                        keyfile=self.client_key, tls_version=ssl.PROTOCOL_TLSv1_2)
                self.client.tls_insecure_set(True)
            self.client.on_log = self.on_log_print
            x=self.client.connect(host=self.mqtt_host, port=int(self.mqtt_port))

        except Exception as e:
            logger.error(str(e))
            return False
        self.connected = True
        return True

    def on_log_print(self, client, userdata, level, buf):
        logger.info(f"MQTT: {level} {buf}")

    def waiting_connect(self, subscriber_list: list[MqttSubscriber], client_name: str="client" ):
        attempts = 0
        while self.connected == False:
            logger.info("Connecting to MQTT (#" + str(attempts) + ")")
            self.connected = self.connect(subscriber_list, client_name, False)
            if self.connected == False:
                time.sleep(2)
                attempts = attempts + 1
                if attempts > 100:
                    logger.error("Failed 100 attempts to connect to MQTT")
                    return False
            else:
                logger.info("Returning from connect MQTT with result code " + str(self.connected))
        return self.connected

    def publish(self, topic: str, msg: any, quality_of_service: int = 0, publish_timeout: int=3, retain: bool=True):
        result = self.client.publish(topic, msg, qos=quality_of_service, retain=retain)
        try:
            for n in range(publish_timeout * 10):
                if result.is_published():
                    logger.info(f"Sent `{msg}` to topic `{topic}`")
                    return 0
                else:
                    time.sleep(0.1)
            logger.error(f"Failed to send message to topic {topic}: {result}")
            return result.rc
        except Exception as e:
            raise MqttException(e, result.rc if result else None) from e

    def manual_loop(self):
        print(self.client.loop())

    def start_listener(self):
        print("Looping")
        result=self.client.loop_start()  # start the loop
        #print(result)

    def register_disconnect_callback(self, callback_function: Callable[[], None]):
        self.disconnect_callbacks.append(callback_function)

    def handle_disconnect(self):
        for callback in self.disconnect_callbacks:
            callback()


def on_my_callback(topic: str, data: any):
    print("GOT CALLBACK",topic, data)

import time, environ

if __name__ == '__main__':
    api_conn = init_api()
    env = environ.Env()
    mqtt_broker = env.str('MQTT_HOST')
    mqtt_port = env.str('MQTT_PORT')
    mqtt_websocket_port = env.str('MQTT_WEBSOCKET_PORT')
    mqtt_usr = None if "MQTT_USERNAME" not in env else env.str("MQTT_USERNAME")
    mqtt_pwd = None if "MQTT_PASSWORD" not in env else env.str("MQTT_PASSWORD")
    ca_cert = None if "MQTT_CA_CERT" not in env else env.str('MQTT_CA_CERT')
    client_cert = None if "MQTT_CLIENT_CERT" not in env else env.str('MQTT_CLIENT_CERT')
    client_key = None if "MQTT_CLIENT_KEY" not in env else env.str('MQTT_CLIENT_KEY')
    mqtt_certs = {'ca_certificate': ca_cert, 'client_certificate': client_cert, 'client_key': client_key}
    mqttcli=MqttClient(mqtt_broker,mqtt_websocket_port)#,mqtt_usr,mqtt_pwd, mqtt_certs)
    es=EventSubscriber("/marketdata/nordicpower/#",on_my_callback)
    mqttcli.connect( [es], "Feed Listener")
    mqttcli.start_listener()
    print("Going into final loop")
    while 1==1:
        time.sleep(1)
