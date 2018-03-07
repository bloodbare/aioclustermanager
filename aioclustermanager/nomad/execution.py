from aioclustermanager.execution import Execution


class NomadExecution(Execution):

    @property
    def pending(self):
        if self.status == 'pending':
            return True
        else:
            return False

    @property
    def running(self):
        if self.status == 'running':
            return True
        else:
            return False

    @property
    def failed(self):
        if self.status == 'failed':
            return True
        else:
            return False

    @property
    def finished(self):
        if self.status == 'complete':
            return True
        else:
            return False

    @property
    def status(self):
        return self._raw['ClientStatus']

    @property
    def events(self):
        result = []
        for condition in self._raw['TaskStates'][self.id]['Events']:
            result.append((condition['Type'], condition['Time']))
        return result

    @property
    def id(self):
        return self._raw['JobID']
