from aioclustermanager.job_list import JobList
from aioclustermanager.k8s.job import K8SJob


class K8SJobList(JobList):

    def __init__(self, data=None, **kw):
        self._raw = data
        self._jobs = []
        for job in self._raw['items']:
            self._jobs.append(K8SJob(data=job))

    @property
    def total(self):
        return len(self._jobs)

    def values(self):
        return self._jobs
