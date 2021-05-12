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

from parse_input import parse_inits


host_num = 0
posted = 0
spamed = 0
q = queue.Queue()

def get_handler(paths, h):
    class handler(h):
        global host_num
        host_num = host_num

        def get_paths(self):
            return paths

        def do_GET(self):
            global host_num
            print("GET")
            self.send_response(200)
            self.send_header('Content-type', 'text-html')
            self.send_header("host", str(host_num))
            self.end_headers()

        def do_POST(self):
            global host_num
            paths = self.get_paths()
            self.send_response(200)
            self.end_headers()
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            logging.info("in POST: %s", post_body)
            self.wfile.write("ok {}".format(post_body).encode('utf-8'))

            dst = 0
            random.shuffle(paths)
            for path in paths:
                for k in path:
                    sr, me = k.split("/")
                    if sr == self.headers["src"] and me == str(host_num):
                        dst = path[k]
                        break

            logging.debug("host_num=%d, dst=%d", host_num, dst)
            if host_num==dst:
                return
            q.put({"body": post_body, "dst": dst})
    return handler


def post_mes(dst, host_num, body):
    logging.debug("about to start connection 10.0.0.{}".format(dst))
    conn = HTTPConnection("10.0.0.{}".format(dst), 8000)
    conn.set_debuglevel(1)
    logging.debug("posting to 10.0.0.{}".format(dst))
    logging.debug("host_num=%d, dst=%d", host_num, dst)
    conn.request("POST", "", body=body, headers={"src": host_num, "dst": dst})
    response = conn.getresponse()
    logging.debug("STATUS: %s, REASON: %s", response.status, response.reason)
    logging.debug("about to CLOSE connection 10.0.0.{}".format(dst))
    conn.close()


def spam(dst, tickrate, start, lifetime):
    global host_num, spamed
    time.sleep(start)
    start_time = time.time()
    while True:
        time.sleep(tickrate)
        post_mes(dst, host_num, "test")
        spamed += 1
        cur_time = time.time()
        if cur_time - start_time >= lifetime:
            logging.info("%d - %d: stopped" % (host_num, dst))
            return


def poster():
    global host_num, posted
    while True:
        post = q.get()
        try:
            post_mes(post["dst"], host_num, post["body"])
            q.task_done()
            posted += 1
        except:
            logging.error("err: %s", sys.exc_info()[0])


def get_my_addr():
    stream = os.popen("ifconfig | grep -o -e '10\.0\.0\.[0-9]*'")
    res = stream.read()
    if res == '':
        return '0'
    return res


def get_path_init(flows):
    paths = list()
    inits = dict()
    for flow in flows:
        path_with_start, tickrate, start, lifetime = flow[0], flow[1], flow[2], flow[3]
        paths.append(path_with_start[0])
        if path_with_start[1][0] not in inits:
            inits[path_with_start[1][0]] = list()
        inits[path_with_start[1][0]].append((path_with_start[1][1], tickrate, start, lifetime))
    return paths, inits


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler, flows_path="flows"):
    global host_num, posted, spamed
    host_num = int(get_my_addr().split('.')[-1])
    logging.debug("%s", get_my_addr())
    paths, inits = get_path_init(parse_inits(flows_path))
    if host_num in inits:
        logging.info("INITIATOR")
        for init in inits[host_num]:
            p = threading.Thread(target=spam, daemon=True, args=init)
            p.start()
    server_address = ('', 8000)
    httpd = server_class(server_address, get_handler(paths, handler_class))
    threading.Thread(target=poster, daemon=True).start()
    logging.info("RUNNING")
    httpd.serve_forever()
    logging.info("in", posted, "out", spamed)
    q.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='http server doing something.')
    parser.add_argument("--flows", default="flows", help="Flows with path and tickrate, file without extension.")
    parser.add_argument("--log-level", default=logging.INFO, type=lambda x: getattr(logging, x), help="Configure the logging level.")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)

    run(flows_path=args.flows)
