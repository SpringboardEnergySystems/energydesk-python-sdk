import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from functools import partial

logger = logging.getLogger(__name__)

class ProbesHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, callback_readiness, callback_liveness, *args, **kwargs):
        self._callback_readiness = callback_readiness
        self._callback_liveness = callback_liveness
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/readiness' and not self._callback_readiness is None:
            self._callback_readiness()
        if self.path == '/liveness' and not self._callback_liveness is None:
            self._callback_liveness()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

def start_probes_server(port: int, callback_readiness=None, callback_liveness=None):
    handler = partial(ProbesHTTPRequestHandler, callback_readiness, callback_liveness)
    httpd = HTTPServer(('', port), handler)
    httpd.serve_forever()
