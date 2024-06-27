from typing import Union

from kafka.protocol.message import Message
from kafka.record.abc import ABCRecord


def postfix_kafka_topic(kafka_topic: str, kafka_topic_postfix: Union[str, None]) -> str:
    if kafka_topic_postfix is not None:
        return f"{kafka_topic}_{kafka_topic_postfix}"
    else:
        return kafka_topic

def decode_message(message: ABCRecord):
    decoded_headers = [(h[0], h[1].decode('utf-8')) for h in message.headers]
    content = str(message.value.decode('utf-8'))
    return content, decoded_headers