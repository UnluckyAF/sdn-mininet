import os

from mininet.node import RemoteController

class POXBridge( RemoteController ):
    def start( self ):
        self.pox = '%s/pox/pox.py' % os.environ[ 'HOME' ]
        self.cmd(
                self.pox,
                '--verbose openflow.spanning_tree',
                '--no-flood --hold-down',
                'log.level --DEBUG samples.pretty_log',
                'openflow.discovery forwarding.l2_learning info.packet_dump &'
                )
    def stop( self ):
        "Stop POX"
        self.cmd( 'kill %' + self.pox )

controllers = { 'poxbridge': POXBridge }

