from copy import deepcopy

K8S_DELETE = {
    'kind': 'DeleteOptions',
    'propagationPolicy': 'Background'
}


class K8SDelete(object):

    def __init__(self, purge=True):
        self._raw = K8S_DELETE
        # K8S supports multiple ways of dealing with the pods but
        # Foreground does not delete the job until pods are deleted
        # This is a different approach from nomad.
        # https://github.com/kubernetes/kubernetes/blob/release-1.7/staging/src/k8s.io/apimachinery/pkg/apis/meta/v1/types.go#L360-L370  # noqa
        # if purge:
        # 	self._raw['propagationPolicy'] = 'Foreground'

    def payload(self):
        return deepcopy(self._raw)
