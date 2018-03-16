from aioclustermanager.node import Node


class NomadNode(Node):
    @property
    def id(self):
        return self._raw['Name']

    @property
    def hostname(self):
        raise NotImplementedError()
