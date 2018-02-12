from aioclustermanager.job_list import JobList


class NomadJobList(JobList):
    @property
    def total(self):
        return len(self._raw)

    @property
    def items(self):
        return self._raw
