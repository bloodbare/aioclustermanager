class Node:
    """Generic node class."""

    def __init__(self, data=None, **kw):
        self._raw = data

    @property
    def id(self):
        raise NotImplementedError()

    @property
    def hostname(self):
        raise NotImplementedError()
