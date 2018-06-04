from aioclustermanager.job import Job
from aioclustermanager.nomad.const import DEAD, SUCCEEDED
from copy import deepcopy

import json

NOMAD_JOB = {
    "Job": {
        "Constraints": [],
        "ID": "",
        "Name": "",
        "TaskGroups": [{
            "Constraints": None,
            "Name": "aioclustermanager",
            "EphemeralDisk": {
                "Migrate": False,
                "SizeMB": 300,
                "Sticky": False
            },
            "RestartPolicy": {
                "Attempts": 0,
                "Delay": 15000000000,
                "Interval": 60000000000,
                "Mode": "fail"
            },
            "Tasks": [{
                "Config": {
                    "image": ""
                },
                "Constraints": [],
                "Driver": "docker",
                "Env": {},
                "LogConfig": {
                    "MaxFileSizeMB": 10,
                    "MaxFiles": 10
                },
                "Name": "",
                "Resources": {
                    "CPU": 200,
                    "MemoryMB": 300,
                    "Networks": [{
                        "CIDR": "",
                        "Device": "",
                        "DynamicPorts": [{
                            "Label": "db",
                            "Value": 0
                        }],
                        "IP": "",
                        "MBits": 200,
                        "ReservedPorts": None
                    }]
                },
                "Services": [],
                "Templates": [],
                "User": "",
            }]
        }],
        "Type": "batch",
    }
}


class NomadJob(Job):

    @property
    def namespace(self):
        return getattr(self, '_namespace', '')

    @property
    def active(self):
        return self._raw['Status'] not in (DEAD, SUCCEEDED)

    @property
    def finished(self):
        return self._raw['Status'] in (DEAD, SUCCEEDED)

    @property
    def status(self):
        return self._raw['Status']

    @property
    def id(self):
        if self.namespace == '':
            return self._raw['ID']
        elif self._raw['ID'].startswith(self.namespace):
            to_remove = len(self.namespace) + 1
            return self._raw['ID'][to_remove:]

    @property
    def command(self):
        return self._raw['Job']['TaskGroups'][0]['Tasks'][0]['Config']['command']  # noqa

    @property
    def image(self):
        return self._raw['Job']['TaskGroups'][0]['Tasks'][0]['Config']['image']  # noqa

    @property
    def scale(self):
        if 'TaskGroups' in self._raw:
            return self._raw['TaskGroups'][0]['Count']
        else:
            return self._raw['Job']['TaskGroups'][0]['Count']

    @scale.setter
    def scale(self, scale):
        if 'TaskGroups' in self._raw:
            self._raw['TaskGroups'][0]['Count'] = scale
        else:
            self._raw['Job']['TaskGroups'][0]['Count'] = scale

    def rewrap(self):
        self._raw = {
            'Job': self._raw
        }

    def get_payload(self):
        if 'TaskGroups' not in self._raw:
            return
        try:
            return json.loads(
                self._raw['TaskGroups'][0]['Tasks'][0]['Env']['PAYLOAD'])
        except (TypeError, KeyError, json.decoder.JSONDecodeError):
            try:
                task = self._raw['TaskGroups'][0]['Tasks'][0]
                templates = task['Templates']
                template = templates[-1]['EmbeddedTmpl']
                payload = template.split(
                    'cat <<EOF')[-1].split('EOF')[0].strip()
                return json.loads(payload)
            except (TypeError, AttributeError, KeyError,
                    json.decoder.JSONDecodeError):
                pass

    def set_datacenters(self, datacenters):
        self._raw['Job']['Datacenters'] = datacenters

    def create(self, namespace, name, image, **kw):
        job_info = deepcopy(NOMAD_JOB)

        real_job_id = '{}-{}'.format(namespace, name)

        job_info['Job']['ID'] = real_job_id
        job_info['Job']['Name'] = real_job_id
        job_info['Job']['TaskGroups'][0]['Tasks'][0]['Name'] = real_job_id

        job_info['Job']['TaskGroups'][0]['Tasks'][0]['Config']['image'] = image

        if 'nomad_constraints' in kw and kw['nomad_constraints'] is not None:
            job_info['Job']['Constraints'] = kw['nomad_constraints']

        if 'docker_network_mode' in kw and kw['docker_network_mode'] is not None:  # noqa
            job_info['Job']['TaskGroups'][0]['Tasks'][0]['Config']['network_mode'] = kw['docker_network_mode']  # noqa

        if 'volumes' in kw and kw['volumes'] is not None:
            job_info['Job']['TaskGroups'][0]['Tasks'][0]['Config']['volumes'] = kw['volumes']  # noqa

        extend_args = []
        if 'command' in kw and kw['command'] is not None:
            job_info['Job']['TaskGroups'][0]['Tasks'][0]['Config']['command'] = kw['command'][0]  # noqa

            if len(kw['command']) > 1:
                extend_args = kw['command'][1:]

        if 'args' in kw and kw['args'] is not None:
            job_info['Job']['TaskGroups'][0]['Tasks'][0]['Config']['args'] = extend_args + kw['args']  # noqa

        if 'templates' in kw and kw['templates'] is not None:
            job_info['Job']['TaskGroups'][0]['Tasks'][0]['Templates'] = kw['templates']  # noqa

        if 'cpu_limit' in kw and kw['cpu_limit'] is not None:
            job_info['Job']['TaskGroups'][0]['Tasks'][0]['Resources']['CPU'] = kw['cpu_limit']  # noqa

        if 'mem_limit' in kw and kw['mem_limit'] is not None:
            job_info['Job']['TaskGroups'][0]['Tasks'][0]['Resources']['MemoryMB'] = kw['mem_limit']  # noqa

        if 'envvars' in kw and kw['envvars'] is not None:
            job_info['Job']['TaskGroups'][0]['Tasks'][0]['Env'] = kw['envvars']  # noqa

        if 'datacenters' in kw and kw['datacenters'] is not None:
            job_info['Job']['Datacenters'] = kw['datacenters']

        return job_info
