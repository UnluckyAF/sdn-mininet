from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )
        midHost = self.addHost( 'h3' )
        leftSwitch = self.addSwitch( 's3' )

        # Add links
        self.addLink( leftHost, rightHost )
        self.addLink( leftHost, midHost )
        self.addLink( midHost, rightHost )
        self.addLink( leftHost, leftSwitch )
        self.addLink( rightHost, leftSwitch )
        self.addLink( midHost, leftSwitch )


topos = { 'mytopo': ( lambda: MyTopo() ) }
