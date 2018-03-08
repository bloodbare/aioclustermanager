from copy import deepcopy

NOMAD_NAMESPACE = {
    "name": "",
}


class NomadNamespace:

    def __init__(self, name=None, data=None):
        if data is not None:
            self._raw = data
        else:
            self._raw = self.create(
                name)

    def create(self, name):
        namespace_info = deepcopy(NOMAD_NAMESPACE)
        namespace_info['name'] = name
        return namespace_info

    def payload(self):
        return deepcopy(self._raw)
