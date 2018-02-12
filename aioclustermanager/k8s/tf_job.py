from aioclustermanager.job import Job
from copy import deepcopy


K8S_JOB = {
    "kind": "TFJob",
    "metadata": {
        "name": "",
        "namespace": ""
    },
    "spec": {
        "replicaSpecs": [{
            "replicas": 1,
            "tfReplicaType": "WORKER",
            "template": {
                "spec": {
                    "containers": [{
                        "image": "",
                        "name": "",
                        "resources": {
                            "limits": {
                            }
                        }
                    }],
                    "restartPolicy": "OnFailure"
                }
            }
        }, {
            "replicas": 1,
            "tfReplicaType": "MASTER",
            "template": {
                "spec": {
                    "containers": [{
                        "image": "",
                        "name": "",
                        "resources": {
                            "limits": {
                            }
                        }
                    }],
                    "restartPolicy": "OnFailure"
                }
            }
        }, {
            "replicas": 1,
            "tfReplicaType": "PS"
        }]
    }
}


class K8STFJob(Job):
    @property
    def active(self):
        return self._raw['status']['active']

    @property
    def finished(self):
        status = self._raw['status']
        return 'failed' in status or 'succeeded' in status

    @property
    def id(self):
        return self._raw['metadata']['name']

    def create(self, namespace, name, image, **kw):
        job_info = deepcopy(K8S_JOB)
        job_info['metadata']['name'] = name
        job_info['metadata']['namespace'] = namespace
        job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['name'] = name
        job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['image'] = image
        job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['name'] = name
        job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['image'] = image

        if 'command' in kw:
            job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['command'] = kw['command']  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['command'] = kw['command']  # noqa

        if 'args' in kw:
            job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['args'] = kw['args']  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['args'] = kw['args']  # noqa

        if 'mem_limit' in kw:
            job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['resources']['limits']['memory'] = kw['mem_limit']  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['resources']['limits']['memory'] = kw['mem_limit']  # noqa

        if 'cpu_limit' in kw:
            job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['resources']['limits']['cpu'] = kw['cpu_limit']  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['resources']['limits']['cpu'] = kw['cpu_limit']  # noqa

        if 'envs' in kw:
            envlist = []
            for key, value in kw['envs']:
                envlist.append({
                    "name": key,
                    "value": value
                })
            job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['env'] = envlist  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['env'] = envlist  # noqa

        return job_info

    def get_payload(self):
        container = self._raw['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]
        for env in container['env']:
            if env['name'] == 'PAYLOAD':
                data = env['value']
                return data
        return None