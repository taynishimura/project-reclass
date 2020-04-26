from toytopo import ToyTopo
from toydiagram import ToyDiagram

from mininet.net import Mininet
#from mininet.topolib import TreeTopo
#from mininet.cli import CLI


def getRouterNames(mininet): return [h.name for h in mininet.hosts if h.name.startswith('r')]
def getSwitchNames(mininet): return [s.name for s in mininet.switches if s.name.startswith('s')]
def getLinkPairs(mininet): return [(l.intf1.node.name, l.intf2.node.name) for l in mininet.links]


def run():
    "Create Mininet & Visualize it"

    # Create Topology

    mininet = Mininet(topo=ToyTopo())
    #mininet = Mininet( topo=TreeTopo( depth=2, fanout=6 ) )

    # Create Diagram

    toydiagram = ToyDiagram(
      getRouterNames(mininet),
      getSwitchNames(mininet),
      getLinkPairs(mininet)
    )
    toydiagram.visualize()

    # Interact with Network generated from Topology

    #mininet.start()
    #CLI( net )
    #mininet.stop()

if __name__== "__main__":
  run() 
