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
        self.send_response(200)
        cur = int(self.headers["cur"]) + 1
        self.end_headers()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
        print(cur)
        dst = (int(self.headers["host"]) + 2) % 3
        if int(self.headers["host"]) == 1:
            dst = 3
        src = (int(self.headers["host"]) + 1) % 3
        if int(self.headers["host"]) == 2:
            src = 3
        conn = HTTPConnection("10.0.0.{}".format(dst), 8000)
        conn.request("POST", "", headers={"cur": cur, "host": src})
        print(cur)
        response = conn.getresponse()
        print(cur)
        conn.close()
        print(cur)


def run(server_class=HTTPServer, handler_class=handler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    conn = HTTPConnection("10.0.0.2", 8000)
    conn.request("POST", "", headers={"cur": 0, "host": 1})
    response = conn.getresponse()
    conn.close()
    run()
