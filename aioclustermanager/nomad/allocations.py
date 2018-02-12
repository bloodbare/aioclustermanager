import json


class NomadAllocations(object):

    def __init__(self, name=None, data=None):
        if name is not None:
            self.name = name
        else:
            self.name = data['metadata']['name']

    def payload(self):
        return json.dumps(
            {
                'api_version': 'v1',
                'kind': 'Namespace',
                'metadata': {
                    'name': self.name
                }
            }
        )
