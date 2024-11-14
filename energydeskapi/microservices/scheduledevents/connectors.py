import logging
import os
import random
import environ
from energydeskapi.events.kafka_events_authenticated import KafkaClientAuthenticated
from energydeskapi.events.mqtt_events_api import MqttClient
from energydeskapi.events.kafka_events_api import KafkaClient

logger = logging.getLogger(__name__)

def connect_to_mqtt(client_id, subscribers=[]):
    global env, ok, bm
    mqtt_client=None
    env = environ.Env()
    logger.info("Starting thread managing MQTT " + str(env("MQTT_HOST")) + ":" + str(env("MQTT_PORT")))
    mqtt_broker = env.str('MQTT_HOST')
    mqtt_port = env.str('MQTT_PORT')
    mqtt_usr = None if "MQTT_USER" not in env else env.str("MQTT_USER")
    mqtt_pwd = None if "MQTT_PASSWORD" not in env else env.str("MQTT_PASSWORD")
    mqtt_client_id = ("MQTT Kafka Gateway" if "MQTT_CLIENTID" not in env else env.str("MQTT_CLIENTID")) + "_" + str(random.randint(0, 999999))
    ca_cert = None if "MQTT_CA_CERT" not in env else env.str('MQTT_CA_CERT')
    client_cert = None if "MQTT_CLIENT_CERT" not in env else env.str('MQTT_CLIENT_CERT')
    client_key = None if "MQTT_CLIENT_KEY" not in env else env.str('MQTT_CLIENT_KEY')
    use_tls = False if "MQTT_USE_TLS" not in env else env.str('MQTT_USE_TLS').lower() == 'true'
    mqtt_certs = {
        'ca_certificate': ca_cert,
        'client_certificate': client_cert,
        'client_key': client_key
    }
    mqttcli = MqttClient(mqtt_broker, mqtt_port, mqtt_usr, mqtt_pwd, mqtt_certs, force_transport="tcp", use_tls=use_tls)
    # Scheduled only sends data not need to listen
    ok = mqttcli.connect(subscribers, mqtt_client_id)
    if ok == True:
        mqttcli.start_listener()
        mqtt_client = mqttcli
    else:
        logger.error("Could not connect to MQTT. Scheduler *may* need a reconfiguration/restart")
        os._exit(1)
    return mqtt_client


def connect_to_kafka(client_id, subscribers=[]):
    env = environ.Env()
    global ok
    kafka_client = None
    kafka_broker = env.str('KAFKA_HOST')
    kafka_port = env.str('KAFKA_PORT')
    kafka_user = None if 'KAFKA_USER' not in env else env.str('KAFKA_USER')
    kafka_password = None if 'KAFKA_PASSWORD' not in env else  env.str('KAFKA_PASSWORD')
    if kafka_user is None:
        kafkacli= KafkaClient(kafka_broker, kafka_port)
        ok = kafkacli.connect(subscribers, consumer_group=client_id)
    else:
        kafkacli = KafkaClientAuthenticated(kafka_broker, kafka_port, kafka_user, kafka_password)
        ok = kafkacli.connect(subscribers, "Scheduler Kafka producer")
    if ok == True:
        logger.info("Connected to Kafka")
        kafka_client = kafkacli
        kafkacli.start_listener()
    else:
        logger.error("Could not connect to Kafka.  Scheduler *may* need a reconfiguration/restart")
        os._exit(1)
    return kafka_client