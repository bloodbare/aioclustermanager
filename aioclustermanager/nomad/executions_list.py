from aioclustermanager.executions_list import ExecutionList
from aioclustermanager.nomad.execution import NomadExecution


class NomadExecutionList(ExecutionList):

    def process(self):
        for pod in self._raw:
            self._executions.append(NomadExecution(data=pod))

    def statuses(self):
        return [execution.status for execution in self]

    def has_failed_anytime(self):
        for execution in self:
            if execution.failed:
                return True
        return False

    def is_running(self):
        return self[-1].running

    def is_done(self):
        if len(self) > 0:
            return self[-1].finished
        return True
