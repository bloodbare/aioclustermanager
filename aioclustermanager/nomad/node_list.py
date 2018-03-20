
from aioclustermanager.node_list import NodeList
from aioclustermanager.nomad.node import NomadNode


class NomadNodeList(NodeList):

    def __init__(self, data=None, **kw):
        self._raw = data
        self._nodes = []
        for node in self._raw:
            self._nodes.append(NomadNode(data=node))
