
from aioclustermanager.node_list import NodeList
from aioclustermanager.k8s.node import K8SNode


class K8SNodeList(NodeList):

    def __init__(self, data=None, **kw):
        self._raw = data
        self._nodes = []
        for node in self._raw['items']:
            self._nodes.append(K8SNode(data=node))

    @property
    def total(self):
        return len(self._nodes)

    def values(self):
        return self._nodes
