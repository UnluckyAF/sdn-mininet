from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import HTTPConnection
import random
import argparse

key = random.randrange(10) + 1
mod = random.randrange(10) + 1
host_num = -1

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text-html')
        self.send_header("host", str(host_num))
        self.end_headers()
        self.wfile.write("key={}".format(key).encode('utf-8'))

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        post_key = int(self.path.split("/"))
        key = key * post_key % mod
        self.wfile.write("{}".format(key).encode('utf-8'))

        host_num = (int(self.headers["src"]) + 1) % 10
        dst = (int(self.headers["src"]) + 2) % 10 
        conn = HTTPConnection("10.0.0.{}".format(dst + 1), 8000)
        conn.request("POST", "/{}".format(key), headers={"src": host_num})
        response = conn.getresponse()
        print(response.status, response.reason, response.read)
        conn.close()


def run(server_class=HTTPServer, handler_class=handler, init=False):
    if init:
        host_num = 0
        conn = HTTPConnection("10.0.0.2", 8000)
        conn.request("POST", "/{}".format(key), headers={"src": host_num})
        response = conn.getresponse()
        conn.close()
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='http server doing something.')
    parser.add_argument("--init", action="store_true", help="if true the server is an initiator.")
    args = parser.parse_args()
    init = args.init

    run()

