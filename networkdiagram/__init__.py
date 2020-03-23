from diagrams import Diagram, Node
from pathlib import Path
import os

class NetworkDiagram(Diagram):
  "Mingrammer's Diagram object repurposed for network diagrams"

class NetworkNode(Node):
  "Mingrammer's Node object repurposed for network diagrams"

  def _load_icon(self):
    basedir = Path(os.path.abspath(os.path.dirname(__file__)) + "/networkdiagram" )
    return os.path.join(basedir.parent, self._icon_dir, self._icon)