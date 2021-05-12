from functools import partial
from time import time, sleep
from select import poll, POLLIN
from subprocess import Popen, PIPE
import os
import sys
import threading

from mininet.node import CPULimitedHost, RemoteController
from mininet.link import TCLink
from mininet.log import info, setLogLevel, output
from util import decode

from controller import POXBridge
from hard_topo import MyTopo, MyMininet
from parse_input import parse_matrix

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


def runServ(hosts, lock):
    cmd = "%s/hard_server/serv.py --log-level 'DEBUG'" % os.environ['HOME']
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
        h.cmd('kill %' + who)


def runIperfs(flows, net, hosts, seconds, lock):
    lock.acquire()
    flag = runD
    lock.release()
    while flag:
        for i in range(len(flows)):
            h1 = hosts[i]
            for j in range(len(flows[i])):
                if flows[i][j][0] < i:
                    continue
                h2 = hosts[flows[i][j][0]]
                # Start iperfs
                lock.acquire()
                perf = net.iperf( (h1, h2), seconds=seconds )
                lock.release()
                output("%s - %s iperf: %s\n" % (h1.name, h2.name, perf[0]))
                flows[i][j] = (flows[i][j][0], perf[1])
        lock.acquire()
        flag = runD
        lock.release()


def iperfTest( seconds=5, path='matrix.csv' ):
    global runD
    topo = MyTopo()
    net = MyMininet( count=3, topo=topo,
                   host=CPULimitedHost, link=TCLink,
                   controller=partial( RemoteController, ip='127.0.0.1', port=6633 ),
                   autoSetMacs=True, waitConnected=False)
    net.start()
    pox = POXBridge('c0', ip='127.0.0.1', port=6613)
    pox.start()
    sleep(15)
    hosts = net.hosts
    flows = parse_matrix(path)

    info( "Starting test...\n" )
    net.pingAll()
    lock = threading.Lock()
    thread = threading.Thread(target=runIperfs, args=(flows, net, hosts, seconds, lock))
    thread.start()

    outfiles, errfiles = runServ(hosts, lock)
    info( "Monitoring output for", seconds * 10, "seconds\n" )
    for h, line in monitorFiles( errfiles, seconds * 10, timeoutms=500 ):
        if h:
            info( '%s: %s\n' % ( h.name, line ) )

    lock.acquire()
    net.pingAll()
    lock.release()

    lock.acquire()
    stopServ(hosts)
    runD = False
    lock.release()
    thread.join()
    pox.stop()
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    iperfTest()
