def postfix_kafka_topic(kafka_topic: str, kafka_topic_postfix: str) -> str:
    return f"{kafka_topic}_{kafka_topic_postfix}"