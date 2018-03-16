from aioclustermanager.node import Node


class K8SNode(Node):
    @property
    def id(self):
        return self._raw['metadata']['name']

    @property
    def hostname(self):
        return self._raw['metadata']['labels']['kubernetes.io/hostname']
