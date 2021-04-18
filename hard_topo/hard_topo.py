from functools import partial

from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost, RemoteController
from mininet.link import TCLink

class MyTopo( Topo ):
    def build( self ):
        "Create custom topo."

        # Initialize topology
        #Topo.__init__( self )

        # Add hosts and switches
        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
        h3 = self.addHost( 'h3' )
        h4 = self.addHost( 'h4' )
        h5 = self.addHost( 'h5' )
        h6 = self.addHost( 'h6' )
        h7 = self.addHost( 'h7' )
        h8 = self.addHost( 'h8' )
        h9 = self.addHost( 'h9' )
        h10 = self.addHost( 'h10' )
        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )
        s4 = self.addSwitch( 's4' )
        s5 = self.addSwitch( 's5' )
        s6 = self.addSwitch( 's6' )
        s7 = self.addSwitch( 's7' )
        s8 = self.addSwitch( 's8' )
        s9 = self.addSwitch( 's9' )
        s10 = self.addSwitch( 's10' )

        # Add links
        self.addLink( s1, s2, bw=10)
        self.addLink( s1, s3 )
        self.addLink( s1, s4 )
        self.addLink( s1, s5 )
        self.addLink( s1, s7 )

        self.addLink( s2, s3 )
        self.addLink( s2, s8 )

        self.addLink( s4, s5 )
        self.addLink( s4, s7 )
        self.addLink( s4, s8 )
        self.addLink( s4, s9 )
        self.addLink( s4, s10 )

        self.addLink( s5, s6 )
        self.addLink( s5, s10 )

        self.addLink( s6, s7 )

        self.addLink( s7, s10 )

        self.addLink( s8, s9 )

        self.addLink( h1, s1 )
        self.addLink( h2, s2 )
        self.addLink( h3, s3 )
        self.addLink( h4, s4 )
        self.addLink( h5, s5 )
        self.addLink( h6, s6 )
        self.addLink( h7, s7 )
        self.addLink( h8, s8 )
        self.addLink( h9, s9 )
        self.addLink( h10, s10 )

topos = { 'mytopo': MyTopo }

if __name__ == '__main__':
    topo = MyTopo()
    net = Mininet( topo=topo,
	           host=CPULimitedHost, link=TCLink,
                   controller=partial( RemoteController, ip='127.0.0.1', port=6633 ),
                   autoSetMacs=True)
    net.start()
    CLI(net)
    net.stop()

