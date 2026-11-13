"""Serve the TwiML for a two-phone Twilio conference test."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PATH = "/twilio/inbound"
TWIML = b"<Response><Dial><Conference>ScamSquashDemo</Conference></Dial></Response>"


class ConferenceWebhook(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != PATH:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/xml; charset=utf-8")
        self.send_header("Content-Length", str(len(TWIML)))
        self.end_headers()
        self.wfile.write(TWIML)


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", 8766), ConferenceWebhook) as server:
        print(f"Conference webhook listening at http://127.0.0.1:8766{PATH}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
