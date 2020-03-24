# diagram.py
from networkdiagram import NetworkDiagram
from diagrams import Cluster
from networkdiagram.diagrams.switch import Switch
from networkdiagram.diagrams.host import Host
from networkdiagram.diagrams.router import Router

from mininet.net import Mininet
from mininet.clean import cleanup
from mininet.node import Node
from mininet.topo import Topo
from mininet.topolib import TreeTopo
from mininet.cli import CLI

class DepGraph():
    "Deduce subnet groups from the list of routers & list of linked devices"
    
    graph = dict()
    knownDevices = set()

    def __init__(self, links=[], routers=[], switches=[]):
        if len(routers): self.addAllNodes(routers)
        else: self.addAllNodes(switches)

        print (links)
        if len(links): self.addAllLinks(links) # prevent infinite loop
        print (self.graph)

    def findParentNode(self, name):
        return self.findParentNodeInSubtree(self.graph, name)
    
    def findParentNodeInSubtree(self, subtree, name):
        if not len(subtree.keys()):
            return None
        if name in subtree.keys():
            return subtree
        for node in subtree.keys():
            result = self.findParentNodeInSubtree(subtree[node], name)
            if result: return result
        return None
    
    def addAllNodes(self, nodes):
        for n in nodes:
            self.graph[n] = dict()
            self.markKnown(n) # TODO @taytay: test mult routers

    def addAllLinks(self, links):
        while len(links):
            skippedLinks = list()
            for (n1, n2) in links:
                skipped = self.addLink(n1, n2)
                if skipped: skippedLinks.append(skipped)
            links = skippedLinks

    def addLink(self, n1, n2):
        print('adding links: ' + n1 + ' ' + n2)

        if not self.isKnown(n1) and not self.isKnown(n2):
            return (n1, n2)
        elif self.isKnown(n1) and not self.isKnown(n2):
            n1_parent = self.findParentNode(n1)
            n1_parent[n1][n2] = dict()
            self.markKnown(n2)
        elif not self.isKnown(n1) and self.isKnown(n2):
            n2_parent = self.findParentNode(n2)
            n2_parent[n2][n1] = dict()
            self.markKnown(n1)
        else:
            n1_parent = self.findParentNode(n1)
            n2_parent = self.findParentNode(n2)

            # routers should be closer to root
            if self.isRouter(n2):
                n2_parent[n2][n1] = n1_parent[n1]
                del n1_parent[n1]
            else:
                n1_parent[n1][n2] = n2_parent[n2]
                del n2_parent[n2]

    def isKnown(self, name):
        return name in self.knownDevices

    def markKnown(self, device):
        self.knownDevices.add(device)

    def isRouter(self, name):
        return name.startswith('r')

    def isSwitch(self, name):
        return name.startswith('s')

    def isHost(self, name):
        return name.startswith('h')

    def getAllSubnets(self):
        subnets = list()
        return self.getSubnets(self.graph, subnets)

    def getSubnets(self, node, subnets):
        for child in node:
            if self.isRouter(child):
                self.getSubnets(node[child], subnets)
            else:
                devices = self.getDevicesInSubnet(node[child], child)
                subnets.append(devices)
        return subnets

    def getDevicesInSubnet(self, node, name):
        devices = [name]
        for child in node:
            devices += self.getDevicesInSubnet(node[child], child)
        return devices


# Copied from examples/linuxrouter.py
class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


# Copied from examples/linuxrouter.py
class TayTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    def build( self, **_opts ):

        defaultIP = '192.168.1.1/24'  # IP address for r0-eth1
        router = self.addNode( 'r0', cls=LinuxRouter, ip=defaultIP )

        s1, s2, s3, s4 = [ self.addSwitch( s ) for s in ( 's1', 's2', 's3', 's4' ) ]

        self.addLink( s1, router, intfName2='r0-eth1',
                      params2={ 'ip' : defaultIP } )  # for clarity
        self.addLink( s2, router, intfName2='r0-eth2',
                      params2={ 'ip' : '172.16.0.1/12' } )
        self.addLink (s3, s2) # TODO @taytay: diagram flow is awkward when parameters are reversed
        self.addLink (s4, s2)

        h1 = self.addHost( 'h1', ip='192.168.1.100/24',
                           defaultRoute='via 192.168.1.1' )
        h2 = self.addHost( 'h2', ip='172.16.0.100/12',
                           defaultRoute='via 172.16.0.1' )
        h3 = self.addHost( 'h3', ip='172.16.0.101/12',
                           defaultRoute='via 10.0.0.1' )
        h4 = self.addHost( 'h4', ip='172.16.0.102/12',
                           defaultRoute='via 20.0.0.1' )

        for h, s in [ (h1, s1), (h2, s3), (h3, s4), (h4, s4) ]:
            self.addLink( h, s )


#def run():
#    "Test linux router"
try:
    # Create Topology

    net = Mininet( topo=TayTopo() )  # controller is used by s1-s3
    #net = Mininet( topo=TreeTopo( depth=2, fanout=6 ) )

    routerNames = [h.name for h in net.hosts if h.name.startswith('r')]
    switchNames = [s.name for s in net.switches if s.name.startswith('s')]
    links = [ (l.intf1.node.name, l.intf2.node.name) for l in net.links]
    depGraph = DepGraph(links = links, routers = routerNames, switches = switchNames)
    subnets = depGraph.getAllSubnets()

    # Create Diagram

    nodes = dict()
    with NetworkDiagram("Simple Network", show=False):
        with Cluster("gateway"):
            for name in routerNames:
                nodes[name] = Router(name) 

        for subnet in subnets:
            with Cluster(subnet[0]):
                for deviceName in subnet:
                    if deviceName.startswith('s'):
                        nodes[deviceName] = Switch(deviceName)
                    elif deviceName.startswith('h'):
                        nodes[deviceName] = Host(deviceName)
                    else:
                        print ('device is neither a switch nor a router: ', deviceName)
                        #exception?

        for (n1, n2) in links: nodes[n2] >> nodes[n1]


    net.start()
    #print( '*** Routing Table on Router:\n' ) # TODO @taytay: print was info before
    #print( net[ 'r0' ].cmd( 'route' ) )
    CLI( net ) # uncomment to 
    net.stop()

    cleanup()
except:
    print("exited early, cleaning up")
    cleanup()
