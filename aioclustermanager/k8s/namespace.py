from copy import deepcopy

K8S_NAMESPACE = {
    "kind": "Namespace",
    "metadata": {
        "name": "",
    }
}


class K8SNamespace(object):

    def __init__(self, name=None, data=None):
        if data is not None:
            self._raw = data
        else:
            self._raw = self.create(
                name)

    def create(self, name):
        namespace_info = deepcopy(K8S_NAMESPACE)
        namespace_info['metadata']['name'] = name
        return namespace_info

    def payload(self):
        return deepcopy(self._raw)
