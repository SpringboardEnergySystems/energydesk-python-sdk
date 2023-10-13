


class EventSubscriber:
    def __init__(self, topic, callback_function):
        self.topic=topic
        self.callback_function=callback_function
        self.prestrtopic=topic.replace("#","")  # Just used for later loookup

class EventClient:
    def __init__(self):
        self.handler_map={}
    def register_callback(self, event_subscriber):
        self.handler_map[event_subscriber.topic]=event_subscriber

    def lookup_subscribers(self, topic):
        print("looking up in map", self.handler_map)
        subscr=[]
        for v in self.handler_map.values():
            print("Comparing ",topic, v.prestrtopic)
            if topic.find(v.prestrtopic)>=0:
                subscr.append(v)
        return subscr

    def handle_callback(self, topic, message):
        subscribers=self.lookup_subscribers(topic)
        for s in subscribers:
            s.callback_function(topic, message)
