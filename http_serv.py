from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import HTTPConnection

cur = 0

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("cur", str(cur))
        self.send_header("host", "1")
        self.end_headers()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        cur = int(self.headers["cur"]) + 1
        dst = (int(self.headers["host"]) + 2) % 3
        src = (int(self.headers["host"]) + 1) % 3
        conn = HTTPConnection("h{}".format(dst), 8000)
        conn.request("POST", "h{}".format(dst), headers={"cur": cur, "host": src})
        response = conn.getresponse()
        conn.close()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run()
