#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import HTTPConnection
from multiprocessing import Process, Manager

import argparse
import logging
import os
import queue
import random
import sys
import threading
import time


host_num = -1
q = queue.Queue()

class handler(BaseHTTPRequestHandler):
    global host_num
    print(host_num)
    host_num = host_num

    def do_GET(self):
        global host_num
        print("GET")
        self.send_response(200)
        self.send_header('Content-type', 'text-html')
        self.send_header("host", str(host_num))
        self.end_headers()

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
        global host_num
        self.send_response(200)
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        logging.info("in POST: %s", post_body)
        self.wfile.write("ok {}".format(post_body).encode('utf-8'))

        dst = 0
        for k in path:
            sr, me = k.split("/")
            if sr == self.headers["src"] and me == str(host_num):
                dst = path[k]
                break

        logging.debug("host_num=%d, dst=%d", host_num, dst)
        if host_num==dst:
            return
        q.put({"body": post_body, "dst": dst})


def spam(dst):
    global host_num
    while True:
        logging.debug("about to start connection 10.0.0.{}".format(dst))
        conn = HTTPConnection("10.0.0.{}".format(dst), 8000)
        conn.set_debuglevel(1)
        logging.debug("posting to 10.0.0.{}".format(dst))
        logging.debug("host_num=%d, dst=%d", host_num, dst)
        conn.request("POST", "", body="test", headers={"src": host_num, "dst": dst - 1})
        response = conn.getresponse()
        logging.debug("STATUS: %s, REASON: %s", response.status, response.reason)
        time.sleep(0.2)
        logging.debug("about to CLOSE connection 10.0.0.{}".format(dst))
        conn.close()


def poster():
    global host_num
    while True:
        post = q.get()
        try:
            logging.debug("about to start connection 10.0.0.{}".format(post["dst"] + 1))
            conn = HTTPConnection("10.0.0.{}".format(post["dst"] + 1), 8000)
            conn.set_debuglevel(1)
            logging.debug("posting to dst: {}".format(post["dst"]))
            conn.request("POST", "", body=post["body"], headers={"src": host_num, "dst": post["dst"]})
            response = conn.getresponse()
            q.task_done()
            logging.debug("STATUS: %s, REASON: %s", response.status, response.reason)
        except:
            logging.error("err: %s", sys.exc_info()[0])
        logging.debug("about to CLOSE connection 10.0.0.{}".format(post["dst"] + 1))
        conn.close()


def get_my_addr():
    stream = os.popen("ifconfig | grep -o -e '10\.0\.0\.[0-9]*'")
    res = stream.read()
    if res == '':
        return '0'
    return res


def run(server_class=HTTPServer, handler_class=handler, init=-1):
    global host_num
    host_num = int(get_my_addr().split('.')[-1]) - 1
    logging.debug("%s", get_my_addr())
    if init != -1:
        logging.info("INITIATOR")
        p = Process(target=spam, daemon=True, args=(init, ))
        p.start()
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    threading.Thread(target=poster, daemon=True).start()
    logging.info("RUNNING")
    httpd.serve_forever()
    q.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='http server doing something.')
    parser.add_argument("--init", type=int, default=-1, help="pass destination host number to make this host an \
            initiator.")
    parser.add_argument("--log-level", default=logging.INFO, type=lambda x: getattr(logging, x), help="Configure the logging level.")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)
    init = args.init

    run(init=init)
