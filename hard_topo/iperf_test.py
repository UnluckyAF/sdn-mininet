#from time import time
#from select import poll, POLLIN
#from subprocess import Popen, PIPE
import os

from mininet.node import CPULimitedHost, RemoteController
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.util import decode

from controller import POXBridge
from hard_topo import MyTopo, MyMininet

# TODO: использовать мининет, топологию из  hard_topo + добавить pox контроллер
#def monitorFiles( outfiles, seconds, timeoutms ):
#    "Monitor set of files and return [(host, line)...]"
#    devnull = open( '/dev/null', 'w' )
#    tails, fdToFile, fdToHost = {}, {}, {}
#    for h, outfile in outfiles.items():
#        tail = Popen( [ 'tail', '-f', outfile ],
#                      stdout=PIPE, stderr=devnull )
#        fd = tail.stdout.fileno()
#        tails[ h ] = tail
#        fdToFile[ fd ] = tail.stdout
#        fdToHost[ fd ] = h
#    # Prepare to poll output files
#    readable = poll()
#    for t in tails.values():
#        readable.register( t.stdout.fileno(), POLLIN )
#    # Run until a set number of seconds have elapsed
#    endTime = time() + seconds
#    while time() < endTime:
#        fdlist = readable.poll(timeoutms)
#        if fdlist:
#            for fd, _flags in fdlist:
#                f = fdToFile[ fd ]
#                host = fdToHost[ fd ]
#                # Wait for a line of output
#                line = f.readline().strip()
#                yield host, decode( line )
#        else:
#            # If we timed out, return nothing
#            yield None, ''
#    for t in tails.values():
#        t.terminate()
#    devnull.close()  # Not really necessary
def runServ(hosts, inits):
    cmd = "%s/hard_server/serv.py --log-level 'DEBUG'" % os.environ['HOME']
    #init = "--init %d
    for host in hosts:
        if int(host.name[1:]) in inits:
            continue
        host.cmd(cmd)

    for host in hosts:
        if int(host.name[1:]) in inits:
            cmd += " --init %d" % inits[int(host.name[1:])]
            host.cmd(cmd + ' &')


def runIperfs(hosts, seconds):
    for i in range(len(hosts)):
        h1 = hosts[i]
        # Create and/or erase output files
        #outfiles[ h1 ] = '/tmp/%s.out' % h1.name
        #errfiles[ h1 ] = '/tmp/%s.err' % h1.name
        #h.cmd( 'echo >', outfiles[ h1 ] )
        #h.cmd( 'echo >', errfiles[ h1 ] )
        for j in range(i:len(hosts)):
            h2 = hosts[j]
            # Start iperfs
            output("%s - %s iperf: %s\n", h1.name, h2.name, net.iperf( (h1, h2), seconds=seconds ))


# TODO: переделать тест под iperf между всеми парами + метрики
def iperfTest( inits, seconds=5 ):
    topo = MyTopo()
    net = MyMininet( count=3, topo=topo,
                   host=CPULimitedHost, link=TCLink,
                   controller=partial( POXBridge, ip='127.0.0.1', port=6633 ),
                   autoSetMacs=True)
    net.start()
    hosts = net.hosts
    info( "Starting test...\n" )
    #outfiles, errfiles = {}, {}
    runIperfs(hosts, seconds)
    runServ(hosts, inits)
    runIperfs(hosts, seconds)
    #monsec = seconds * (seconds + 1) / 2
    #info( "Monitoring output for", monsec, "seconds\n" )
    #for h, line in monitorFiles( outfiles, seconds, timeoutms=500 ):
    #    if h:
    #        info( '%s: %s\n' % ( h.name, line ) )
    #for h in hosts:
    #    h.cmd('kill %ping')
    net.stop()


if __name__ == '__main__':
    setLogLevel('debug')
    iperfTest({
        1: 2
        })
