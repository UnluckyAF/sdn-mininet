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
                'openflow.discovery forwarding.l2_learning info.packet_dump',
                '>', "/tmp/c0out",
                '2>', "/tmp/c0err",
                '&'
                )
    def stop( self ):
        "Stop POX"
        self.cmd( 'kill %' + self.pox )

class POXBridgeMulti( RemoteController ):
    def start( self ):
        self.cmd("export PYTHONPATH=$PYTHONPATH:~/hard_server;")
        self.pox = '%s/pox/pox.py' % os.environ[ 'HOME' ]
        self.cmd(
                self.pox,
                '--verbose openflow.spanning_tree',
                '--no-flood --hold-down',
                'log.level --DEBUG samples.pretty_log',
                'openflow.discovery path info.packet_dump',
                '>', "/tmp/c0Multiout",
                '2>', "/tmp/c0Multierr",
                '&'
                )
    def stop( self ):
        "Stop POX"
        self.cmd( 'kill %' + self.pox )


controllers = { 'poxbridge': POXBridge, 'poxbriedgemulti': POXBridgeMulti}

