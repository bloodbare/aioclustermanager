from aioclustermanager.execution import Execution
from aioclustermanager.nomad.const import FAILED, PENDING, RUNNING, SUCCEEDED


class NomadExecution(Execution):

    @property
    def pending(self):
        if self.status == PENDING:
            return True
        else:
            return False

    @property
    def running(self):
        if self.status == RUNNING:
            return True
        else:
            return False

    @property
    def failed(self):
        if self.status == FAILED:
            return True
        else:
            return False

    @property
    def finished(self):
        if self.status == SUCCEEDED:
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

    @property
    def internal_id(self):
        return self._raw['ID']
