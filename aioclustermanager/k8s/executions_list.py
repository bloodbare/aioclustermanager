from aioclustermanager.executions_list import ExecutionList
from aioclustermanager.k8s.execution import K8SExecution


class K8SExecutionList(ExecutionList):

    def process(self):
        for pod in self._raw['items']:
            self._executions.append(K8SExecution(data=pod))

    def statuses(self):
        return [execution.status for execution in self]

    def has_failed_anytime(self):
        for execution in self:
            if execution.status == 'Failed':
                return True
        return False

    def is_running(self):
        for execution in self:
            if execution.status == 'Running':
                return True
        return False

    def is_done(self):
        for execution in self:
            if execution.status == 'Succeeded':
                return True
        return False
