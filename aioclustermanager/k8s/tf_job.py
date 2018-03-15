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
                    # XXX are we sure we want to restart these jobs?
                    # what if they restart continuously on bad code?
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
        # have to love the nesting here...
        job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['name'] = name  # noqa
        job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['image'] = image  # noqa
        job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['name'] = name  # noqa
        job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['image'] = image  # noqa

        if 'entrypoint' in kw and kw['entrypoint'] is not None:
            job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['entrypoint'] = kw['entrypoint']  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['entrypoint'] = kw['entrypoint']  # noqa

        if 'command' in kw and kw['command'] is not None:
            job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['command'] = kw['command']  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['command'] = kw['command']  # noqa

        if 'args' in kw and kw['args'] is not None:
            job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['args'] = kw['args']  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['args'] = kw['args']  # noqa

        if 'mem_limit' in kw and kw['mem_limit'] is not None:
            job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['resources']['limits']['memory'] = kw['mem_limit']  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['resources']['limits']['memory'] = kw['mem_limit']  # noqa

        if 'cpu_limit' in kw and kw['cpu_limit'] is not None:
            job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['resources']['limits']['cpu'] = kw['cpu_limit']  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['resources']['limits']['cpu'] = kw['cpu_limit']  # noqa

        if 'volumes' in kw and kw['volumes'] is not None:
            job_info['spec']['replicaSpecs'][0]['template']['spec']['volumes'] = kw['volumes']  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['volumes'] = kw['volumes']  # noqa

        if 'volumeMounts' in kw and kw['volumeMounts'] is not None:
            job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['volumeMounts'] = kw['volumeMounts']  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['volumeMounts'] = kw['volumeMounts']  # noqa

        if 'envFrom' in kw and kw['envFrom'] is not None:
            job_info['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]['envFrom'] = kw['envFrom']  # noqa
            job_info['spec']['replicaSpecs'][1]['template']['spec']['containers'][0]['envFrom'] = kw['envFrom']  # noqa

        if 'envs' in kw and kw['envs'] is not None:
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
        container = self._raw['spec']['replicaSpecs'][0]['template']['spec']['containers'][0]  # noqa
        for env in container['env']:
            if env['name'] == 'PAYLOAD':
                data = env['value']
                return data
        return None
