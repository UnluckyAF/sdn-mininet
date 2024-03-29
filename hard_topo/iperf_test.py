from functools import partial
from time import time, sleep
from select import poll, POLLIN
from subprocess import Popen, PIPE
import os
import sys
import threading

from mininet.node import CPULimitedHost, RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import info, setLogLevel, output, error
from util import decode

from controller import POXBridge, POXBridgeMulti, initPox
from hard_topo import MyTopo, MyMininet
from parse_input import parse_matrix, parse_inits
from custom_flow_table import create_table

runD = True

def monitorFiles( outfiles, seconds, timeoutms ):
    "Monitor set of files and return [(host, line)...]"
    devnull = open( '/dev/null', 'w' )
    tails, fdToFile, fdToHost = {}, {}, {}
    for h, outfile in outfiles.items():
        tail = Popen( [ 'tail', '-f', outfile ],
                      stdout=PIPE, stderr=devnull )
        fd = tail.stdout.fileno()
        tails[ h ] = tail
        fdToFile[ fd ] = tail.stdout
        fdToHost[ fd ] = h
    # Prepare to poll output files
    readable = poll()
    for t in tails.values():
        readable.register( t.stdout.fileno(), POLLIN )
    # Run until a set number of seconds have elapsed
    endTime = time() + seconds
    while time() < endTime:
        fdlist = readable.poll(timeoutms)
        if fdlist:
            for fd, _flags in fdlist:
                f = fdToFile[ fd ]
                host = fdToHost[ fd ]
                # Wait for a line of output
                line = f.readline().strip()
                yield host, decode( line )
        else:
            # If we timed out, return nothing
            yield None, ''
    for t in tails.values():
        t.terminate()
    devnull.close()  # Not really necessary


def runServ(hosts, lock, use_path_alg):
    cmd = "%s/hard_server/serv.py --log-level 'DEBUG'" % os.environ['HOME']
    if use_path_alg:
        cmd += " --use_path_alg"
    outfiles, errfiles = {}, {}
    for host in hosts:
        # Create and/or erase output files
        outfiles[ host ] = '/tmp/%s.out' % host.name
        errfiles[ host ] = '/tmp/%s.err' % host.name
        lock.acquire()
        host.cmd( 'echo >', outfiles[ host ] )
        host.cmd( 'echo >', errfiles[ host ] )
        host.cmdPrint(cmd,
                '>', outfiles[ host],
                '2>', errfiles[ host ],
                '&')
        lock.release()
    return outfiles, errfiles


def stopServ(hosts):
    who = "%s/hard_server/serv.py" % os.environ['HOME']
    for h in hosts:
        o = h.cmd('kill %' + who)
        output("killed %s %s" % (time(), o))


def runIperfs(flows, net, hosts, seconds, lock, metrics, dead_sw, cv):
    lock.acquire()
    flag = runD
    lock.release()
    while flag:
        for i in range(len(flows)):
            if len(metrics) < i + 1:
                metrics.append(list())
            h1 = hosts[i]
            for j in range(len(flows[i])):
                if flows[i][j][0] < i:
                    for flow in flows[flows[i][j][0]]:
                        if flow[0] == i:
			    flows[i][j] = (flows[i][j][0], flow[1])
                            if len(metrics[i]) < j + 1:
                                metrics[i].append((flows[i][j][0], 0))
                    continue
                h2 = hosts[flows[i][j][0]]
                # Start iperfs
                err = False
                perf = ['1000 1000']
                if h1.name != "h%d" % dead_sw:
                    lock.acquire()
                    try:
                        perf = net.iperf( (h1, h2), seconds=seconds, fmt='m' )
                    except:
                        output("error in iperf %s %s: %s" % (h1.name, h2.name, sys.exc_info()))
                        err = True
                    lock.release()
                    if err:
                        continue
                else:
                    err = True
                output("%s - %s iperf: %s\n" % (h1.name, h2.name, perf))
                flows[i][j] = (flows[i][j][0], float(perf[0].split(' ')[0]))
                if len(metrics[i]) < j + 1:
                    metrics[i].append((flows[i][j][0], [float(perf[0].split(' ')[0])]))
                else:
                    metrics[i][j][1].append(float(perf[0].split(' ')[0]))
                lock.acquire()
                flag = runD
                lock.release()
                if not flag:
                    return

        cv.acquire()
        cv.wait(5)
        cv.release()


def run_flow_table_manager(flows, passed_flows, lock, cv):
    lock.acquire()
    flag = runD
    lock.release()
    while flag:
        create_table(flows, passed_flows)
        cv.acquire()
        cv.wait(10)
        flag = runD
        cv.release()


def write_metrics(metrics, name="metrics"):
    with open(name, "w") as f:
        for i in range(len(metrics)):
            for pair in metrics[i]:
                if pair[0] > i:
                    f.write("%s - %s %s" % (i, pair[0], pair[1]))


def dump_flows(host, lock, n):
    lock.acquire()
    sleep(10)
    for i in range(n):
        host.cmd("ovs-ofctl dump-flows s%d > s%d.out" % (i+1, i+1))
    lock.release()


def iperfTest( seconds=5, matrix_path='matrix.csv', inits_path='flows', sw=0 ):
    global runD
    topo = MyTopo()
    net = MyMininet( count=3, topo=topo,
                   host=CPULimitedHost, link=TCLink,
                   controller=partial( RemoteController, ip='127.0.0.1', port=6633 ),
                   autoSetMacs=True, waitConnected=False)
    net.start()
    pox = POXBridgeMulti('c0', ip='127.0.0.1', port=6613)
    #pox = initPox(sw)('c0', ip='127.0.0.1', port=6613)
    pox.start()
    sleep(15)
    hosts = net.hosts
    flows = parse_matrix(matrix_path)

    info( "Starting test...\n" )
    #net.pingAllFull()
    #net.pingAll()
    lock = threading.Lock()
    cv = threading.Condition(lock)
    metrics = list()
    passed_flows = parse_inits(inits_path)
    flowTable = threading.Thread(target=run_flow_table_manager, args=(flows, passed_flows, lock, cv))
    flowTable.start()

    outfiles, errfiles = runServ(hosts, lock, True)
    #info( "Monitoring output for", seconds * 10, "seconds\n" )
    #for h, line in monitorFiles( errfiles, seconds * 10, timeoutms=500 ):
    #    if h:
    #        info( '%s: %s\n' % ( h.name, line ) )
    sleep(5)
    thread = threading.Thread(target=runIperfs, args=(flows, net, hosts, seconds, lock, metrics, sw, cv))
    thread.start()
    sleep(300)
    #lock.acquire()
    #output("ping 10")
    #hosts[3].cmd("ping -c 5 10.0.0.10 > ping")
    #lock.release()
    #dump_flows(hosts[0], lock, len(hosts))
    #sleep(100)
    #lock.acquire()
    #output("ping 10")
    #hosts[4].cmd("ping -c 5 10.0.0.10 > ping2")
    #lock.release()
    #lock.acquire()
    #net.pingAllFull()
    #net.pingAll()
    #lock.release()
    #CLI(net)

    lock.acquire()
    stopServ(hosts)
    runD = False
    lock.release()
    flowTable.join()
    thread.join()

    write_metrics(metrics)
    metrics = list()
    pox.stop()
    info( "Stop dijkstra, start spanning tree\n" )

    pox = POXBridge('c0', ip='127.0.0.1', port=6613)
    pox.start()
    sleep(15)


    #os.remove("flow_table")
    runD = True
    outfiles, errfiles = runServ(hosts, lock, False)
    sleep(5)
    thread = threading.Thread(target=runIperfs, args=(flows, net, hosts, seconds, lock, metrics, sw, cv))
    thread.start()
    sleep(300)
    ###lock.acquire()
    ###net.pingAllFull()
    ###net.pingAll()
    ###lock.release()
    ###CLI(net)

    lock.acquire()
    stopServ(hosts)
    runD = False
    lock.release()
    thread.join()

    write_metrics(metrics, name="metrics2")
    metrics = list()

    pox.stop()
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    iperfTest()
