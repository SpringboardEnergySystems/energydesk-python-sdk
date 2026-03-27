import logging
import socket


class SafeRemoteHandler(logging.Handler):
    """
    Wrapper for remote logging handlers (e.g., Logstash TCP) that swallows
    network errors to prevent noisy warnings and hangs when the remote
    collector is down or unreachable.
    """
    def __init__(self, handler):
        super().__init__(handler.level if hasattr(handler, "level") else logging.NOTSET)
        self._handler = handler

    def emit(self, record):
        """Emit a log record, swallowing network/connection errors."""
        try:
            self._handler.emit(record)
        except (ConnectionRefusedError, BrokenPipeError, OSError, socket.error):
            # Swallow network errors to avoid noisy logs when ELK is down
            pass
        except Exception:
            # Catch-all for unexpected errors; log silently if possible
            try:
                logging.getLogger(__name__).debug(
                    "SafeRemoteHandler emit failed", exc_info=True
                )
            except Exception:
                pass

    def close(self):
        """Close the handler, swallowing any errors during shutdown."""
        try:
            self._handler.close()
        except Exception:
            pass
        super().close()

    def setFormatter(self, fmt):
        """Delegate formatter setting to wrapped handler."""
        self._handler.setFormatter(fmt)

    def setLevel(self, level):
        """Delegate level setting to wrapped handler."""
        super().setLevel(level)
        self._handler.setLevel(level)

