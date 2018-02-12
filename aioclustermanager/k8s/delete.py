from copy import deepcopy

K8S_DELETE = {
    'kind': 'DeleteOptions',
    'propagationPolicy': 'Background'
}


class K8SDelete(object):

    def __init__(self):
        self._raw = K8S_DELETE

    def payload(self):
        return deepcopy(self._raw)
