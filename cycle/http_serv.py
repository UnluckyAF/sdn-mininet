from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import HTTPConnection

cur = 0

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text-html')
        self.send_header("cur", str(cur))
        self.send_header("host", "1")
        self.end_headers()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
        cur = int(self.headers["cur"]) + 1
        dst = (int(self.headers["host"]) + 2) % 3
        if int(self.headers["host"]) == 1:
            dst = 3
        src = (int(self.headers["host"]) + 1) % 3
        if int(self.headers["host"]) == 2:
            src = 3
        print(dst)
        conn = HTTPConnection("10.0.0.{}".format(dst), 8000)
        conn.request("POST", "", headers={"cur": cur, "host": src})
        print(dst)
        response = conn.getresponse()
        print(dst)
        conn.close()
        print(dst)


def run(server_class=HTTPServer, handler_class=handler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run()

