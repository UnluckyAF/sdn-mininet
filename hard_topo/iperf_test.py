from functools import partial
from time import time, sleep
from select import poll, POLLIN
from subprocess import Popen, PIPE
import sys
import os

from mininet.node import CPULimitedHost, RemoteController
from mininet.link import TCLink
from mininet.log import info, setLogLevel, output
from util import decode

from controller import POXBridge
from hard_topo import MyTopo, MyMininet


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


def runServ(hosts):
    cmd = "%s/hard_server/serv.py --log-level 'DEBUG'" % os.environ['HOME']
    outfiles, errfiles = {}, {}
    for host in hosts:
        # Create and/or erase output files
        outfiles[ host ] = '/tmp/%s.out' % host.name
        errfiles[ host ] = '/tmp/%s.err' % host.name
        host.cmd( 'echo >', outfiles[ host ] )
        host.cmd( 'echo >', errfiles[ host ] )
        host.cmdPrint(cmd,
                '>', outfiles[ host],
                '2>', errfiles[ host ],
                '&')
    return outfiles, errfiles


def stopServ(hosts):
    who = "%s/hard_server/serv.py" % os.environ['HOME']
    for h in hosts:
        h.cmd('kill %' + who)


def runIperfs(net, hosts, seconds):
    for i in range(len(hosts)):
        h1 = hosts[i]
        for j in range(i+1,len(hosts)):
            h2 = hosts[j]
            # Start iperfs
            output("%s - %s iperf: %s\n" % (h1.name, h2.name, net.iperf( (h1, h2), seconds=seconds )))


def iperfTest( seconds=5 ):
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
    info( "Starting test...\n" )
    net.pingAll()
    #runIperfs(net, hosts, seconds)
    outfiles, errfiles = runServ(hosts)
    info( "Monitoring output for", seconds * 10, "seconds\n" )
    for h, line in monitorFiles( outfiles, seconds * 10, timeoutms=500 ):
        if h:
            info( '%s: %s\n' % ( h.name, line ) )
    net.pingAll()
    runIperfs(net, hosts, seconds)
    #monsec = seconds * (seconds + 1) / 2
    #info( "Monitoring output for", monsec, "seconds\n" )
    #for h, line in monitorFiles( outfiles, seconds, timeoutms=500 ):
    #    if h:
    #        info( '%s: %s\n' % ( h.name, line ) )
    pox.stop()
    stopServ(hosts)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    iperfTest()
