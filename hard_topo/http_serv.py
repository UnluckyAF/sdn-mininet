from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import HTTPConnection
import random
import argparse


key = random.randrange(10) + 1
mod = random.randrange(10) + 1
host_num = -1

class handler(BaseHTTPRequestHandler):
    global key, mod, host_num
    print(key, mod, host_num)
    key = key
    mod = mod
    host_num = host_num
    print(key, mod, host_num)


    def do_GET(self):
        global key, mod, host_num
        print("GET")
        self.send_response(200)
        self.send_header('Content-type', 'text-html')
        self.send_header("host", str(host_num))
        self.end_headers()
        self.wfile.write("key={}".format(key).encode('utf-8'))

    def do_POST(self):
        path = {
            "0/1": 2,
            "1/2": 0,
            "2/0": 3,
            "0/3": 4,
            "3/4": 5,
            "4/5": 6,
            "5/6": 3,
            "6/3": 7,
            "3/7": 8,
            "7/8": 3,
            "8/3": 9
        }
        global key, mod, host_num
        print("POST")
        self.send_response(200)
        self.end_headers()
        print(self.path.split("/"))
        post_key = int(self.path.split("/")[1])
        #print(key, post_key, mod)
        key = key * post_key % mod
        print(key, post_key, mod)
        self.wfile.write("{}".format(key).encode('utf-8'))

        host_num = int(self.headers["dst"])

        dst = 0
        for k in path:
            sr, me = k.split("/")
            if sr == self.headers["src"] and me == str(host_num):
                dst = path[k]
                break
        #dst = (int(self.headers["src"]) + 2) % 10
        print(host_num, dst, key)
        conn = HTTPConnection("10.0.0.{}".format(dst + 1), 8000)
        conn.request("POST", "/{}".format(key + 1), headers={"src": host_num, "dst": dst})
        response = conn.getresponse()
        print(response.status, response.reason, response.read)
        conn.close()


def run(server_class=HTTPServer, handler_class=handler, init=False):
    global key, mod, host_num
    if init:
        print("INITIATOR")
        host_num = 0
        conn = HTTPConnection("10.0.0.2", 8000)
        conn.request("POST", "/{}".format(key + 1), headers={"src": host_num, "dst": 1})
        response = conn.getresponse()
        conn.close()
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    print("RUNNING")
    httpd.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='http server doing something.')
    parser.add_argument("--init", action="store_true", help="if true the server is an initiator.")
    args = parser.parse_args()
    init = args.init

    run(init=init)
