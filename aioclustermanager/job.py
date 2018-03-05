class Job:
    """Generic job class."""

    def __init__(self, namespace=None, name=None, image=None, data=None, **kw):
        if data is not None:
            self._raw = data
        else:
            self._raw = self.create(
                namespace,
                name=name,
                image=image,
                **kw)

    @property
    def active(self):
        raise NotImplementedError()

    @property
    def finished(self):
        raise NotImplementedError()

    @property
    def id(self):
        raise NotImplementedError()

    def get_payload(self):
        raise NotImplementedError()

    def payload(self):
        return self._raw
