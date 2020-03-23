
from networkdiagram import NetworkNode


class Host(NetworkNode):
    _provider = "taynet"
    _icon_dir = "resources/host"
    fontcolor = "#ffffff"

    #
    _type = "."
    _icon = "host.png"
