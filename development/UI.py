from http import server
from urllib import parse


class UIRequestHandler (server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "debug.html":
            pass
        elif self.path.startswith("getstate"):
            

    def do_POST(self):
        if self.path.startswith("getstate"):
            length = int(self.headers.getheader('content-length'))
            field_data = self.rfile.read(length)
            fields = parse.parse_qs(field_data)


if __name__ == "__main__":
    uiserver = server.HTTPServer(("127.0.0.1", 80), UIRequestHandler)
    try:
        uiserver.serve_forever()
        print("Server started")
    except KeyboardInterrupt:
        print("Server stopped")
