import json
from copy import deepcopy
from aioclustermanager.job import Job


NOMAD_JOB = {
    "Job": {
        "AllAtOnce": False,
        "Constraints": [],
        "ID": "",
        "Name": "",
        "TaskGroups": [{
            "Constraints": None,
            "Count": 1,
            "Name": "aioclustermanager",
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
                    "MemoryMB": 300
                },
                "Services": [],
                "Templates": [],
                "User": "",
                "Vault": None
            }]
        }],
        "Type": "service",
    }
}


class NomadJob(Job):

    @property
    def active(self):
        return self._raw['Status'] not in ('dead', 'complete')

    # @property
    # def finished(self):
    #     return self._raw['Status'] in ('dead', 'complete')

    # @property
    # def id(self):
    #     return self._raw['ID']

    # @property
    # def allocation(self):
    #     return self._raw['allocation']

    # def get_payload(self):
    #     if 'TaskGroups' not in self._raw:
    #         return
    #     try:
    #         return json.loads(
    #             self._raw['TaskGroups'][0]['Tasks'][0]['Env']['PAYLOAD'])
    #     except (TypeError, KeyError, json.decoder.JSONDecodeError):
    #         try:
    #             task = self._raw['TaskGroups'][0]['Tasks'][0]
    #             templates = task['Templates']
    #             template = templates[-1]['EmbeddedTmpl']
    #             payload = template.split(
    #                 'cat <<EOF')[-1].split('EOF')[0].strip()
    #             return json.loads(payload)
    #         except (TypeError, AttributeError, KeyError,
    #                 json.decoder.JSONDecodeError):
    #             pass

    # def set_datacenters(self, datacenters):
    #     self._raw['Job']['Datacenters'] = datacenters

    # def create(self, namespace, name, image, **kw):
    #     """
    #     nomad_constraints
    #     docker_network_mode
    #     """
    #     job_info = deepcopy(NOMAD_JOB)

    #     real_job_id = '{}-{}'.format(namespace, name)

    #     job_info['Job']['ID'] = real_job_id
    #     job_info['Job']['Name'] = real_job_id
    #     job_info['Job']['TaskGroups'][0]['Tasks'][0]['Name'] = real_job_id

    #     job_info['Job']['TaskGroups'][0]['Tasks'][0]['Config']['image'] = image

    #     if 'nomad_constraints' in kw and kw['nomad_constraints'] is not None:
    #         job_info['Job']['Constraints'] = kw['nomad_constraints']

    #     if 'docker_network_mode' in kw and kw['docker_network_mode'] is not None:
    #         job_info['Job']['TaskGroups'][0]['Tasks'][0]['Config']['network_mode'] = kw['docker_network_mode']  # noqa

    #     if 'volumes' in kw and kw['volumes'] is not None:
    #         job_info['Job']['TaskGroups'][0]['Tasks'][0]['Config']['volumes'] = kw['volumes']  # noqa

    #     if 'command' in kw and kw['command'] is not None:
    #         job_info['Job']['TaskGroups'][0]['Tasks'][0]['Config']['command'] = ' '.join(kw['command'])  # noqa

    #     if 'args' in kw and kw['args'] is not None:
    #         job_info['Job']['TaskGroups'][0]['Tasks'][0]['Config']['args'] = kw['args']  # noqa

    #     if 'templates' in kw and kw['templates'] is not None:
    #         job_info['Job']['TaskGroups'][0]['Tasks'][0]['Templates'] = kw['templates']  # noqa

    #     if 'cpu_limit' in kw and kw['cpu_limit'] is not None:
    #         job_info['Job']['TaskGroups'][0]['Tasks'][0]['Resources']['CPU'] = kw['cpu_limit']  # noqa

    #     if 'mem_limit' in kw and kw['mem_limit'] is not None:
    #         job_info['Job']['TaskGroups'][0]['Tasks'][0]['Resources']['MemoryMB'] = kw['mem_limit']  # noqa

    #     if 'envs' in kw and kw['envs'] is not None:
    #         job_info['Job']['TaskGroups'][0]['Tasks'][0]['Env'] = kw['envs']  # noqa

    #     if 'datacenters' in kw and kw['datacenters'] is not None:
    #         job_info['Job']['Datacenters'] = kw['datacenters']

    #     return job_info

