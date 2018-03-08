from aioclustermanager.job import Job
from copy import deepcopy

K8S_JOB = {
    "kind": "Job",
    "metadata": {
        "name": "",
        "namespace": ""
    },
    "spec": {
        "template": {
            "metadata": {
                "name": ""
            },
            "spec": {
                "containers": [
                    {
                        "name": "",
                        "image": "",
                        "resources": {
                            "limits": {
                            }
                        }
                    }
                ],
                "restartPolicy": "Never"
            }
        }
    }
}


class K8SJob(Job):
    @property
    def active(self):
        status = self._raw['status']
        return False if 'active' not in status else status['active']

    @property
    def finished(self):
        status = self._raw['status']
        return 'failed' in status or 'succeeded' in status

    @property
    def id(self):
        return self._raw['metadata']['name']

    @property
    def command(self):
        return self._raw['spec']['template']['spec']['containers'][0]['command']  # noqa

    @property
    def image(self):
        return self._raw['spec']['template']['spec']['containers'][0]['image']

    def create(self, namespace, name, image, **kw):
        job_info = deepcopy(K8S_JOB)
        job_info['metadata']['name'] = name
        job_info['metadata']['namespace'] = namespace
        job_info['spec']['template']['metadata']['name'] = name
        job_info['spec']['template']['spec']['containers'][0]['name'] = name
        job_info['spec']['template']['spec']['containers'][0]['image'] = image

        if 'command' in kw:
            job_info['spec']['template']['spec']['containers'][0]['command'] = kw['command']  # noqa

        if 'args' in kw:
            job_info['spec']['template']['spec']['containers'][0]['args'] = kw['args']  # noqa

        if 'mem_limit' in kw:
            job_info['spec']['template']['spec']['containers'][0]['resources']['limits']['memory'] = kw['mem_limit']  # noqa

        if 'cpu_limit' in kw:
            job_info['spec']['template']['spec']['containers'][0]['resources']['limits']['cpu'] = kw['cpu_limit']  # noqa

        if 'envs' in kw:
            envlist = []
            for key, value in kw['envs']:
                envlist.append({
                    "name": key,
                    "value": value
                })
            job_info['spec']['template']['spec']['containers'][0]['env'] = envlist  # noqa

        return job_info

    def get_payload(self):
        container = self._raw['spec']['template']['spec']['containers'][0]
        for env in container['env']:
            if env['name'] == 'PAYLOAD':
                data = env['value']
                return data
        return None
