from typing import Callable


class EventSubscriber:
    def __init__(self, topic: str, callback_function: Callable[[str, str, list[tuple[str, any]]], None]):
        self.topic=topic
        self.callback_function=callback_function
        self.prestrtopic=topic.replace("#","")  # Just used for later loookup

class EventClient:
    def __init__(self):
        self.handler_map={}
    def register_callback(self, event_subscriber: EventSubscriber):
        self.handler_map[event_subscriber.topic]=event_subscriber

    def lookup_subscribers(self, topic: str):
        subscr=[]
        for v in self.handler_map.values():
            if topic.find(v.prestrtopic)>=0:
                subscr.append(v)
        return subscr

    def handle_callback(self, topic: str, message: str, headers: list[tuple[str, any]]=[]):
        subscribers=self.lookup_subscribers(topic)
        for s in subscribers:
            s.callback_function(topic, message, headers)


def lookup_header(headers: list[tuple[str, any]], field: str) -> any:
    d=dict(headers)
    if field in d:
        return d[field]
    return None