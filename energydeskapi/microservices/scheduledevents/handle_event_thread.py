import logging
import time
from typing import Any

from energydeskapi.events.queue_with_put_back import QueueWithPutBack
from energydeskapi.microservices.scheduledevents.handle_event import EventHandler

logger = logging.getLogger(__name__)


class HandleEventThread:
    def __init__(self, queue: QueueWithPutBack[Any], send_system: EventHandler):
        self._queue = queue
        self._send_system = send_system

    def listen_to_queue(self):
        logger.info("Wait a moment to give time to the terminating pods to terminate")
        time.sleep(5)
        logger.info("Listening to queue")
        while True:
            try:
                logger.info("Ready for the mext message  queue.")
                self._queue.handle_one_message_with(self._handle_one_message)
            except Exception as e:
                self.take_a_pause(e)


    def take_a_pause(self, e):
        wait_seconds = 1
        logger.error(f"Error sending message to MQTT. Wait {wait_seconds} second(s) and retry {e}")
        time.sleep(wait_seconds)

    def _handle_one_message(self, item: Any):
        logger.error("Handling a message from the MQTT sending queue got wrong message type ")
