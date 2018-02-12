from aioclustermanager.execution import Execution


class K8SExecution(Execution):

    @property
    def pending(self):
        if self._raw['status']['phase'] == 'Pending':
            return True
        else:
            return False

    @property
    def running(self):
        if self._raw['status']['phase'] == 'Running':
            return True
        else:
            return False

    @property
    def failed(self):
        if self._raw['status']['phase'] == 'Failed':
            return True
        else:
            return False

    @property
    def status(self):
        return self._raw['status']['phase']

    @property
    def events(self):
        result = []
        for condition in self._raw['status']['conditions']:
            result.append((condition['type'], condition['lastTransitionTime']))
        return result

    @property
    def id(self):
        return self._raw['metadata']['name']
