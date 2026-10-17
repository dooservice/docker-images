"""The page of whatever address the proxy could not serve: from its catch-all router when no
environment is routed there, or from its errors middleware when the environment answered
502 to 504, or 500 in production. Either way the browser asked for the original address,
which is in `Host`."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .card import Card, Cards, Host
from .cases import WORDING, Case
from .constants import FAILED_PATH, FINAL_STATUS, HEALTH_PATH, PORT, RETRY_AFTER_SECONDS, WAITING_STATUS
from .page import Page


class StatusHandler(BaseHTTPRequestHandler):
    cards = Cards()
    page = Page()
    server_version = "dooservice-status"
    sys_version = ""

    def do_GET(self) -> None:
        self.answer(with_body=True)

    def do_HEAD(self) -> None:
        self.answer(with_body=False)

    def do_POST(self) -> None:
        self.answer(with_body=True)

    def answer(self, with_body: bool) -> None:
        self.close_connection = True
        if self.path == HEALTH_PATH:
            self.send(200, b"ok", "text/plain", with_body)
            return
        host = Host.of(self.headers.get("Host", ""))
        card = self.cards.of(host)
        if self.path.partition("?")[0] == FAILED_PATH and card.case == Case.NOT_RESPONDING:
            card = Card(Case.FAILING)
        final = WORDING[card.case].final
        self.send(
            FINAL_STATUS if final else WAITING_STATUS,
            self.page.render(card, host).encode(),
            "text/html; charset=utf-8",
            with_body,
        )

    def send(self, status: int, body: bytes, content_type: str, with_body: bool) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Robots-Tag", "noindex")
        if status == WAITING_STATUS:
            self.send_header("Retry-After", RETRY_AFTER_SECONDS)
        self.end_headers()
        if with_body:
            self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


class StatusServer:
    def __init__(self, port: int = PORT) -> None:
        self.server = ThreadingHTTPServer(("0.0.0.0", port), StatusHandler)

    def serve(self) -> None:
        self.server.serve_forever()
