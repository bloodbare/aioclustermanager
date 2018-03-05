from dateutil.parser import parse


class Execution:
    """Generic pod class."""

    def __init__(self, data=None):
        self._raw = data

    @property
    def id(self):
        raise NotImplementedError()

    @property
    def pending(self):
        raise NotImplementedError()

    @property
    def running(self):
        raise NotImplementedError()

    @property
    def status(self):
        raise NotImplementedError()

    @property
    def events(self):
        raise NotImplementedError()

    def get_payload(self):
        raise NotImplementedError()

    def payload(self):
        return self._raw

    def sort_status_executions(self):
        result = sorted(self.events, key=lambda x: parse(x[1]))
        return result
