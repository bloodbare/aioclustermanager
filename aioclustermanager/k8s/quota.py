from aioclustermanager.utils import generate_word
from copy import deepcopy

K8S_LIMITS = {
    "kind": "ResourceQuota",
    "metadata": {
        "name": "",
        "namespace": ""
    },
    "spec": {
        "hard": {
            "requests.cpu": "",
            "requests.memory": "",
            "limits.cpu": "",
            "limits.memory": ""
        }
    }
}


class K8SQuota(object):

    def __init__(
            self, namespace=None, name=None, max_cpu=None,
            max_memory=None, data=None):
        if data is not None:
            self._raw = data
        else:
            if name is None:
                name = generate_word(10)
            self._raw = self.create(
                namespace,
                name=name,
                max_memory=max_memory,
                max_cpu=max_cpu)

    @property
    def id(self):
        return self._raw['metadata']['name']

    def create(self, namespace, name, max_memory, max_cpu):
        limit_info = deepcopy(K8S_LIMITS)
        limit_info['metadata']['name'] = name
        limit_info['metadata']['namespace'] = namespace
        limit_info['spec']['hard']['requests.cpu'] = max_cpu
        limit_info['spec']['hard']['requests.memory'] = max_memory
        limit_info['spec']['hard']['limits.cpu'] = max_cpu
        limit_info['spec']['hard']['limits.memory'] = max_memory
        return limit_info

    def payload(self):
        return deepcopy(self._raw)
