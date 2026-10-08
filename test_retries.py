import json
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from main import fetch_weather


class TemporaryFailureHandler(BaseHTTPRequestHandler):
    request_count = 0

    def do_GET(self):
        type(self).request_count += 1

        if type(self).request_count == 1:
            self.send_error(503, "Temporary failure")
            return

        body = json.dumps({"test": "success"}).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


class RetryTests(unittest.TestCase):
    def test_recovers_after_temporary_failure(self):
        TemporaryFailureHandler.request_count = 0
        server = HTTPServer(("127.0.0.1", 0), TemporaryFailureHandler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            url = f"http://127.0.0.1:{server.server_port}/weather"

            result = fetch_weather(60.1699, 24.9384, url=url)

            self.assertEqual(result, {"test": "success"})
            self.assertEqual(TemporaryFailureHandler.request_count, 2)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()