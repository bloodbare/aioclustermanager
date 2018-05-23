from copy import deepcopy

K8S_SCALE = {
    "kind": "Scale",
    "metadata": {
        "name": "",
        "namespace": ""
    },
    "spec": {
        "replicas": 0
    }
}


class K8SScale(object):

    def __init__(
            self, namespace, name, scale):
        self._raw = self.create(
            namespace,
            name=name,
            scale=scale)

    @property
    def id(self):
        return self._raw['metadata']['name']

    def create(self, namespace, name, scale):
        scale_info = deepcopy(K8S_SCALE)
        scale_info['metadata']['name'] = name
        scale_info['metadata']['namespace'] = namespace
        scale_info['spec']['replicas'] = scale
        return scale_info

    def payload(self):
        return deepcopy(self._raw)
