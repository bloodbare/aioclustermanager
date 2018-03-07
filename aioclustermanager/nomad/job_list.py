from aioclustermanager.job_list import JobList
from aioclustermanager.nomad.job import NomadJob


class NomadJobList(JobList):

    def __init__(self, data=None, namespace='', **kw):
        self._raw = data
        self._jobs = []
        for job in self._raw:
            job_obj = NomadJob(data=job)
            job_obj._namespace = namespace
            self._jobs.append(job_obj)

    @property
    def total(self):
        return len(self._jobs)

    def values(self):
        return self._jobs
