class NodeList:
    """Generic Node class."""

    def __init__(self, data=None, **kw):
        self._raw = data
        self._nodes = []

    def __len__(self):
        return len(self.values())

    def __iter__(self):
        for node in self.values():
            yield node

    def __setitem__(self, key, value):
        self._nodes[key] = value

    def __getitem__(self, key):
        return self._nodes[key]

    @property
    def total(self):
        return len(self._nodes)

    def values(self):
        return self._nodes
