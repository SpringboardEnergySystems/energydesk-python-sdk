import queue
from dataclasses import dataclass
from typing import Callable, TypeVar, Generic

U = TypeVar('U')


@dataclass(frozen=True)
class QueueWithPutBackStatus:
    times_item_was_put_back: int

# a queue to communicate between two threads, one reading from an external source (montel, tradingtech), the'
# other sending to MQTT, The idea is that if there are problem sending an item to MQTT, the MQTT thread can set it back
# to the queue and send it again later
class QueueWithPutBack(Generic[U]):
    def __init__(self):
        self._main_queue = queue.Queue()
        # no need of locks for putback_item which is only used by the listening thread
        self._putback_item = None
        self._times_item_was_put_back = 0

    def put(self, item: U):
        self._main_queue.put(item)

    def handle_one_message_with(self, callback: Callable[[U, QueueWithPutBackStatus], None]) -> None:
        item = self._get()
        try:
            callback(item, QueueWithPutBackStatus(self._times_item_was_put_back))
        except Exception as e:
            self._put_back(item)
            raise

    def _get(self) -> U:
        if self._putback_item is not None:
            to_return = self._putback_item
            self._putback_item = None
            self._times_item_was_put_back += 1
            return to_return
        else:
            self._times_item_was_put_back = 0
            return self._main_queue.get()

    def _put_back(self, item: U) -> None:
        if self._putback_item is None:
            self._putback_item = item
        else:
            # it does not make sense to have more than one put back item.
            # in case there is a put back item you continue to try to work with that until there is no more exception
            raise ValueError("There is already an item that was put back in the queue")
