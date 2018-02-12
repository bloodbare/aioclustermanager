

class ExecutionList:
    """Generic job class."""

    def __init__(self, data=None, **kw):
        self._raw = data
        self._executions = []
        self.process()

    def process(self):
        raise NotImplementedError()

    def values(self):
        return self._executions

    def __len__(self):
        return len(self._executions)

    def __iter__(self):
        for execution in self._executions:
            yield execution

    def __setitem__(self, key, value):
        self._executions[key] = value

    def __getitem__(self, key):
        return self._executions[key]
