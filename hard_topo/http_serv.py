from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import HTTPConnection
from multiprocessing import Process
import argparse
import logging
import random
import time


#key = random.randrange(10) + 1
#mod = random.randrange(10) + 1
host_num = -1

class handler(BaseHTTPRequestHandler):
    global host_num
    #print(key, mod, host_num)
    print(host_num)
    #key = key
    #mod = mod
    host_num = host_num
    #print(key, mod, host_num)


    def do_GET(self):
        #global key, mod, host_num
        global host_num
        print("GET")
        self.send_response(200)
        self.send_header('Content-type', 'text-html')
        self.send_header("host", str(host_num))
        self.end_headers()
        #self.wfile.write("key={}".format(key).encode('utf-8'))

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
        #global key, mod, host_num
        global host_num
        print("POST")
        self.send_response(200)
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        logging.info("in POST: %s", post_body)
        #print(self.path.split("/"))
        #post_key = int(self.path.split("/")[1])
        #print(key, post_key, mod)
        #key = key * post_key % mod
        #print(key, post_key, mod)
        self.wfile.write("ok {}".format(post_body).encode('utf-8'))

        if host_num == -1:
            host_num = int(self.headers["dst"])
        elif host_num != int(self.headers["dst"]):
            logging.error("wrong host dst from %d", self.headers["src"])

        dst = 0
        for k in path:
            sr, me = k.split("/")
            if sr == self.headers["src"] and me == str(host_num):
                dst = path[k]
                break
        #dst = (int(self.headers["src"]) + 2) % 10
        #print(host_num, dst, key)
        logging.debug("host_num=%d, dst=%d", host_num, dst) 
        logging.debug("about to start connection 10.0.0.%d", dst + 1)
        conn = HTTPConnection("10.0.0.{}".format(dst + 1), 8000)
        conn.set_debuglevel(1)
        logging.debug("posting to 10.0.0.%d, dst: %d", dst + 1, dst)
        conn.request("POST", "", body=post_body, headers={"src": host_num, "dst": dst})
        response = conn.getresponse()
        logging.debug("STATUS: %s, REASON: %s", response.status, response.reason)
        #logging.debug("RESPONSE: %s", response.read())
        #print(response.status, response.reason, response.read)
        logging.debug("about to CLOSE connection 10.0.0.%d", dst + 1)
        conn.close()

def spam():
    global host_num
    logging.debug("about to start connection 10.0.0.2")
    conn = HTTPConnection("10.0.0.2", 8000)
    conn.set_debuglevel(1)
    while True:
        logging.debug("posting to 10.0.0.2, dst: 1")
        conn.request("POST", "", body="test", headers={"src": host_num, "dst": 1})
        response = conn.getresponse()
        logging.debug("STATUS: %s, REASON: %s", response.status, response.reason)
        #logging.debug("RESPONSE: %s", response.read())
        #print(response.status, response.reason, response.read)
        time.sleep(0.2)
    logging.debug("about to CLOSE connection 10.0.0.2")
    conn.close()


def run(server_class=HTTPServer, handler_class=handler, init=False):
    global host_num
    if init:
        logging.info("INITIATOR")
        host_num = 0
        p = Process(target=spam, daemon=True)
        p.start()
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    logging.info("RUNNING")
    httpd.serve_forever()
    #p.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='http server doing something.')
    parser.add_argument("--init", action="store_true", help="if true the server is an initiator.")
    parser.add_argument("--log-level", default=logging.INFO, type=lambda x: getattr(logging, x), help="Configure the logging level.")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)
    init = args.init

    run(init=init)
