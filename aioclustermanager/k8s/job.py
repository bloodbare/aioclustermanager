from aioclustermanager.job import Job
from copy import deepcopy

import json

K8S_JOB = {
    "kind": "Job",
    "metadata": {
        "name": "",
        "namespace": ""
    },
    "spec": {
        "backoffLimit": 1,
        "restartPolicy": "Never",
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
                        },
                        "imagePullPolicy": "IfNotPresent"
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

        if 'entrypoint' in kw and kw['entrypoint'] is not None:
            job_info['spec']['template']['spec']['containers'][0]['entrypoint'] = kw['entrypoint']  # noqa

        if 'command' in kw and kw['command'] is not None:
            job_info['spec']['template']['spec']['containers'][0]['command'] = kw['command']  # noqa

        if 'args' in kw and kw['args'] is not None:
            job_info['spec']['template']['spec']['containers'][0]['args'] = kw['args']  # noqa

        if 'mem_limit' in kw and kw['mem_limit'] is not None:
            job_info['spec']['template']['spec']['containers'][0]['resources']['limits']['memory'] = kw['mem_limit']  # noqa

        if 'cpu_limit' in kw and kw['cpu_limit'] is not None:
            job_info['spec']['template']['spec']['containers'][0]['resources']['limits']['cpu'] = kw['cpu_limit']  # noqa

        if 'volumes' in kw and kw['volumes'] is not None:
            job_info['spec']['template']['spec']['volumes'] = kw['volumes']

        if 'volumeMounts' in kw and kw['volumeMounts'] is not None:
            job_info['spec']['template']['spec']['containers'][0]['volumeMounts'] = kw['volumeMounts']  # noqa

        if 'envFrom' in kw and kw['envFrom'] is not None:
            job_info['spec']['template']['spec']['containers'][0]['envFrom'] = kw['envFrom']  # noqa

        if 'envvars' in kw and kw['envvars'] is not None:
            envlist = []
            for key, value in kw['envvars'].items():
                envlist.append({
                    "name": key,
                    "value": value
                })
            job_info['spec']['template']['spec']['containers'][0]['env'] = envlist  # noqa

        return job_info

    def get_payload(self):
        container = self._raw['spec']['template']['spec']['containers'][0]
        for env in container.get('env') or []:
            if env['name'] == 'PAYLOAD':
                data = env['value']
                return json.loads(data)
        return None
