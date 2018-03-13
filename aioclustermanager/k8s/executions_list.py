from aioclustermanager.executions_list import ExecutionList
from aioclustermanager.k8s.const import FAILED, RUNNING, SUCCEEDED
from aioclustermanager.k8s.execution import K8SExecution


class K8SExecutionList(ExecutionList):

    def process(self):
        for pod in self._raw['items']:
            self._executions.append(K8SExecution(data=pod))

    def statuses(self):
        return [execution.status for execution in self]

    def has_failed_anytime(self):
        for execution in self:
            if execution.status == FAILED:
                return True
        return False

    def is_running(self):
        for execution in self:
            if execution.status == RUNNING:
                return True
        return False

    def is_done(self):
        for execution in self:
            if execution.status == SUCCEEDED:
                return True
        return False
