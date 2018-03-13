class JobList:
    """Generic job class."""

    def __init__(self, data=None, **kw):
        self._raw = data

    @property
    def values(self):
        raise NotImplementedError()

    def __len__(self):
        return len(self.values())

    def __iter__(self):
        for job in self.values():
            yield job

    def schedulled_pods(self):
        for key, value in self.items():
            if len(value) > 0:
                # XXX work with both nomad and k8s?
                schedulled = list(filter(lambda x: x[0] == 'PodScheduled', value[0].events))  # noqa
