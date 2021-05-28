from functools import partial
import re

from mininet.node import ( Host, OVSKernelSwitch, DefaultController)
from mininet.log import output, debug
from mininet.link import Link, Intf
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost, RemoteController
from mininet.link import TCLink
from mininet.util import waitListening

from parse_input import parse_matrix

class MyTopo( Topo ):
    def build( self ):
        "Create custom topo."
        switches = list()
        links = parse_matrix("matrix2.csv")
        for i in range(len(links)):
            h = self.addHost( 'h%s' % str(i+1) )
            s = self.addSwitch( 's%s' % str(i+1) )
            self.addLink( h, s)
            switches.append(s)

        for i in range(len(links)):
            node = links[i]
            for link in node:
		self.addLink(switches[i], switches[link[0]], bw=link[1])
        

topos = { 'mytopo': MyTopo }


def median(lst):
    if len(lst) == 0:
        return None

    lst.sort()
    if len(lst) % 2 == 0:
        return (lst[len(lst) // 2 - 1] + lst[len(lst) // 2]) / 2


class MyMininet(Mininet):
    def __init__( self, topo=None, switch=OVSKernelSwitch, host=Host,
                  controller=DefaultController, link=Link, intf=Intf,
                  build=True, xterms=False, cleanup=False, ipBase='10.0.0.0/8',
                  inNamespace=False,
                  autoSetMacs=False, autoStaticArp=False, autoPinCpus=False,
                  listenPort=None, waitConnected=False, count=1 ):
        super(MyMininet, self).__init__(topo, switch, host, controller, link, intf, build,
                         xterms, cleanup, ipBase, inNamespace, autoSetMacs,
                         autoStaticArp, autoPinCpus, listenPort, waitConnected)
        self.count = count
    def pingFull( self, hosts=None, timeout=None ):
        """Ping between all specified hosts and return all data.
           hosts: list of hosts
           timeout: time to wait for a response, as string
           returns: all ping data; see function body."""
        # should we check if running?
        # Each value is a tuple: (src, dsd, [all ping outputs])
        all_outputs = []
        if not hosts:
            hosts = self.hosts
            output( '*** Ping: testing ping reachability\n' )
        for node in hosts:
            output( '%s -> ' % node.name )
            for dest in hosts:
                if node != dest:
                    opts = ''
                    if timeout:
                        opts = '-W %s' % timeout
                    result = node.cmd( 'ping -c%d %s %s' % (self.count, opts, dest.IP()) )
                    outputs = self._parsePingFull( result )
                    sent, received, rttmin, rttavg, rttmax, rttdev = outputs
                    all_outputs.append( (node, dest, outputs) )
                    output( ( '%s ' % dest.name ) if received else 'X ' )
            output( '\n' )
        output( "*** Results: \n" )
        for outputs in all_outputs:
            src, dest, ping_outputs = outputs
            sent, received, rttmin, rttavg, rttmax, rttdev = ping_outputs
            output( " %s->%s: %s/%s, " % (src, dest, sent, received ) )
            output( "rtt min/avg/max/mdev %0.3f/%0.3f/%0.3f/%0.3f ms\n" %
                    (rttmin, rttavg, rttmax, rttdev) )
        return all_outputs

    #@staticmethod
    #def _parseIperf( iperfOutput ):
    #    """Parse iperf output and return bandwidth.
    #       iperfOutput: string
    #       returns: result string"""
    #    r = r'([\d\.]+ \w+/sec)'
    #    m = re.findall( r, iperfOutput )
    #    if m:
    #        tmp = map(lambda x: x.split(' ')[0], m)
    #        tmp2 = list()
    #        for elem in tmp:
    #            if float(elem) != 0:
    #                tmp2.append(elem)
    #        mmin = min(map(float, tmp2))
    #        mmax = max(map(float, tmp2))
    #        avg = sum(map(float, tmp2)) / len(tmp2)
    #        med = median(map(float, tmp2))
    #        return ([mmin, avg, mmax, med], m[-1])
    #    else:
    #        # was: raise Exception(...)
    #        error( 'could not parse iperf output: ' + iperfOutput )
    #        return []

    ## XXX This should be cleaned up

    #def iperf( self, hosts=None, l4Type='TCP', udpBw='10M', fmt=None,
    #           seconds=5, port=5001):
    #    """Run iperf between two hosts.
    #       hosts: list of hosts; if None, uses first and last hosts
    #       l4Type: string, one of [ TCP, UDP ]
    #       udpBw: bandwidth target for UDP test
    #       fmt: iperf format argument if any
    #       seconds: iperf time to transmit
    #       port: iperf port
    #       returns: two-element array of [ server, client ] speeds
    #       note: send() is buffered, so client rate can be much higher than
    #       the actual transmission rate; on an unloaded system, server
    #       rate should be much closer to the actual receive rate"""
    #    hosts = hosts or [ self.hosts[ 0 ], self.hosts[ -1 ] ]
    #    assert len( hosts ) == 2
    #    client, server = hosts
    #    output( '*** Iperf: testing', l4Type, 'bandwidth between',
    #            client, 'and', server, '\n' )
    #    server.cmd( 'killall -9 iperf' )
    #    iperfArgs = 'iperf -p %d ' % port
    #    bwArgs = ''
    #    if l4Type == 'UDP':
    #        iperfArgs += '-u '
    #        bwArgs = '-b ' + udpBw + ' '
    #    elif l4Type != 'TCP':
    #        raise Exception( 'Unexpected l4 type: %s' % l4Type )
    #    if fmt:
    #        iperfArgs += '-f %s ' % fmt
    #    server.sendCmd( iperfArgs + '-s' )
    #    if l4Type == 'TCP':
    #        if not waitListening( client, server.IP(), port ):
    #            raise Exception( 'Could not connect to iperf on port %d'
    #                             % port )
    #    cliout = client.cmd( iperfArgs + '-t %d -c ' % seconds +
    #                         server.IP() + ' ' + bwArgs )
    #    debug( 'Client output: %s\n' % cliout )
    #    servout = ''
    #    # We want the last *b/sec from the iperf server output
    #    # for TCP, there are two fo them because of waitListening
    #    count = 2 if l4Type == 'TCP' else 1
    #    while len( re.findall( '/sec', servout ) ) < count:
    #        servout += server.monitor( timeoutms=5000 )
    #    server.sendInt()
    #    servout += server.waitOutput()
    #    debug( 'Server output: %s\n' % servout )
    #    parsed_serv = self._parseIperf( servout )
    #    parsed_client = self._parseIperf( cliout )
    #    result = [parsed_serv[0], parsed_client[0]]
    #    if l4Type == 'UDP':
    #        result.insert( 0, udpBw )
    #    output( '*** Results (min, avg, max, median): %s\n' % result )
    #    return (result, parsed_serv[1])


if __name__ == '__main__':
    topo = MyTopo()
    net = MyMininet( count=3, topo=topo,
                   host=CPULimitedHost, link=TCLink,
                   controller=partial( RemoteController, ip='127.0.0.1', port=6633 ),
                   autoSetMacs=True)
    net.start()
    CLI(net)
    net.stop()

