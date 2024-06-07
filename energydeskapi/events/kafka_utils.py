from typing import Union

def postfix_kafka_topic(kafka_topic: str, kafka_topic_postfix: Union[str, None]) -> str:
    if kafka_topic_postfix is not None:
        return f"{kafka_topic}_{kafka_topic_postfix}"
    else:
        return kafka_topic