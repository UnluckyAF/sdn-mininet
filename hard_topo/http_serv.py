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

from parse_input import parse_inits, path_to_map


host_num = 0
posted = 0
spamed = 0
q = queue.Queue()

#def get_handler(paths, h):
class MyHandler(BaseHTTPRequestHandler):
    global host_num
    host_num = host_num

    #def get_paths(self):
    #    return paths

    def do_GET(self):
        global host_num
        print("GET")
        self.send_response(200)
        self.send_header('Content-type', 'text-html')
        self.send_header("host", str(host_num))
        self.end_headers()

    def do_POST(self):
        global host_num
        #paths = self.get_paths()
        self.send_response(200)
        self.end_headers()
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        logging.info("in POST: %s", post_body)
        self.wfile.write("ok {}".format(post_body).encode('utf-8'))

        str_path = self.headers["path"]
        path = path_to_map(str_path)[0]
        print(path)
        #random.shuffle(paths)
        #path = paths[flow_id]
        dst = 0
        for k in path:
            sr, me = k.split("/")
            if sr == self.headers["src"] and me == str(host_num):
                dst = path[k]
                break

        logging.debug("host_num=%d, dst=%d", host_num, dst)
        if host_num==dst or dst == 0:
            return
        q.put({"body": post_body, "dst": dst, "path": str_path})


def post_mes(dst, host_num, body, path):
    logging.debug("about to start connection 10.0.0.{}".format(dst))
    conn = HTTPConnection("10.0.0.{}".format(dst), 8000)
    conn.set_debuglevel(1)
    logging.debug("posting to 10.0.0.{}".format(dst))
    logging.debug("host_num=%d, dst=%d", host_num, dst)
    logging.debug(path)
    conn.request("POST", "", body=body, headers={"src": host_num, "dst": dst, "path": path})
    response = conn.getresponse()
    logging.debug("STATUS: %s, REASON: %s", response.status, response.reason)
    logging.debug("about to CLOSE connection 10.0.0.{}".format(dst))
    conn.close()


def map_to_path(path, src, dst):
    str_path = ''
    key = str(src) + "/" + str(dst)
    start_key = key
    str_path = key
    while key in path:
        src = dst
        dst = path[key]
        str_path += "/" + str(dst)
        key = str(src) + "/" + str(dst)
        if key == start_key:
            break
    return str_path


def get_dst(path, src):
    for key in path.keys():
        f, s = key.split("/")
        if int(f) == src:
            return int(s)
    return 0


def spam(dst, tickrate, start, lifetime, flow_id, paths):
    global host_num, spamed
    time.sleep(start)
    start_time = time.time()
    print("DEBUG", dst, paths[flow_id], paths, flow_id)
    if paths[flow_id] != {} and str(host_num) + '/' + str(dst) not in paths[flow_id]:
        dst = get_dst(paths[flow_id], host_num)
    print("DEBUG", dst, paths[flow_id])
    path = map_to_path(paths[flow_id], host_num, dst)
    while True:
        try:
            print(paths, flow_id)
            post_mes(dst, host_num, "test", path)
            spamed += 1
            cur_time = time.time()
            if cur_time - start_time >= lifetime:
                logging.info("%d - %d: stopped" % (host_num, dst))
                return
            time.sleep(tickrate)
        except:
            logging.error("err: %s", sys.exc_info())


def poster():
    global host_num, posted
    while True:
        post = q.get()
        try:
            post_mes(post["dst"], host_num, post["body"], post["path"])
            q.task_done()
            posted += 1
        except:
            logging.error("err: %s", sys.exc_info())


def get_my_addr():
    stream = os.popen("ifconfig | grep -o -e '10\.0\.0\.[0-9]*'")
    res = stream.read()
    if res == '':
        return '0'
    return res


def get_path_init(flows):
    paths = list()
    inits = dict()
    i = 0
    for flow in flows:
        path_with_start, tickrate, start, lifetime = flow[0], flow[1], flow[2], flow[3]
        paths.append(path_with_start[0])
        if path_with_start[1][0] not in inits:
            inits[path_with_start[1][0]] = list()
        inits[path_with_start[1][0]].append((path_with_start[1][1], tickrate, start, lifetime, i))
        i += 1
    return paths, inits


def fill_custom_paths(paths, flow_table='flow_table'):
    while True:
        time.sleep(15)
        res = list()
        with open(flow_table, "r") as f:
            i = 0
            for line in f:
                new_path = path_to_map(line)[0]
                logging.debug(new_path)
                map_path = paths[i]
                for key, val in new_path.items():
                    map_path[key] = val
                res.append(map_path)
                i += 1
        if len(res) > 0:
            paths = res


def unpack(init, paths):
    return (init[0], init[1], init[2], init[3], init[4], paths)


#TODO: here filling with custom paths happens once, but must happen all the time with intervals
def run(server_class=HTTPServer, handler_class=MyHandler, flows_path="flows", use_path_alg=False):
    global host_num, posted, spamed
    host_num = int(get_my_addr().split('.')[-1])
    logging.debug("%s", get_my_addr())
    paths, inits = get_path_init(parse_inits(flows_path))
    #TODO: move this part to thread?
    if use_path_alg:
        threading.Thread(target=fill_custom_paths, daemon=True, args=(paths, )).start()
    #paths = fill_custom_paths(paths)
    if host_num in inits:
        logging.info("INITIATOR")
        for init in inits[host_num]:
            p = threading.Thread(target=spam, daemon=True, args=unpack(init, paths))
            p.start()
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    threading.Thread(target=poster, daemon=True).start()
    logging.info("RUNNING")
    httpd.serve_forever()
    logging.info("in", posted, "out", spamed)
    q.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='http server doing something.')
    parser.add_argument("--flows", default="flows", help="Flows with path and tickrate, file without extension.")
    parser.add_argument("--use_path_alg", default=False, action='store_true', help="Use path algorithm (dijkstra).")
    parser.add_argument("--log-level", default=logging.INFO, type=lambda x: getattr(logging, x), help="Configure the logging level.")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)

    run(flows_path=args.flows, use_path_alg=args.use_path_alg)
