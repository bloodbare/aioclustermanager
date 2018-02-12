from aioclustermanager.job_list import JobList
from aioclustermanager.k8s.tf_job import K8STFJob


class K8STFJobList(JobList):

    def __init__(self, data=None, **kw):
        self._raw = data
        self._jobs = []
        for job in self._raw['items']:
            self._jobs.append(K8STFJob(data=job))

    @property
    def total(self):
        return len(self._jobs)

    def values(self):
        return self._jobs
