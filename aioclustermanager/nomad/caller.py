from aioclustermanager.nomad import const
from aioclustermanager.nomad.executions_list import NomadExecutionList
from aioclustermanager.nomad.job import NomadJob
from aioclustermanager.nomad.job_list import NomadJobList
from aioclustermanager.nomad.namespace import NomadNamespace

import asyncio
import logging

# from aioclustermanager.utils import convert

logger = logging.getLogger(__name__)

WATCH_OPS = {
    'job': 'http://{endpoint}/v1/job/{namespace}-{name}/allocations',
    'namespace': None
}

GET_OPS = {
    'list_jobs': 'http://{endpoint}/v1/jobs',
    'job': 'http://{endpoint}/v1/job/{namespace}-{name}',
    'executions': 'http://{endpoint}/v1/job/{namespace}-{name}/allocations'
}

POST_OPS = {
    'job': 'http://{endpoint}/v1/jobs'
}

DELETE_OPS = {
    'job': 'http://{endpoint}/v1/job/{namespace}-{name}?purge=true'
}


class NomadCaller:
    _type = 'nomad'
    constants = const

    def __init__(self, endpoint, datacenters, session):
        self.endpoint = endpoint
        self.session = session
        self.datacenters = datacenters

    @property
    def type(self):
        return self._type

    # Namespaces, implementation using prefix jobs

    async def get_namespace(self, namespace):
        return NomadNamespace(name=namespace)

    async def create_namespace(self, namespace):
        return True

    async def delete_namespace(self, namespace):
        jobs = await self.list_jobs(namespace)
        for job in jobs:
            await self.delete_job(namespace, job.id)
        return True

    async def wait_added(self, kind, namespace, name=None):
        url = WATCH_OPS[kind]
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        return await self.watch(url, value='Started')  # correct status?

    async def wait_deleted(self, kind, namespace, name=None):
        url = WATCH_OPS[kind]
        if url is None:
            return False
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        return await self.watch(url, value='Deleted')  # correct status?

    async def define_quota(self, namespace, cpu_limit=None, mem_limit=None):
        # Only supported on nomad enterprise
        pass

    async def get_job(self, namespace, name):
        url = GET_OPS['job']
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        params = {}
        result = await self.get(url, params)
        if result is None:
            return None
        else:
            job_obj = NomadJob(data=result)
            job_obj._namespace = namespace
            return job_obj

    async def get_tfjob(self, namespace, name):
        # TODO
        return None

    async def get_job_executions(self, namespace, name):
        url = GET_OPS['executions']
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        params = {}
        result = await self.get(url, params)
        if result is None:
            return None
        else:
            return NomadExecutionList(data=result)

    async def delete_job(self, namespace, name, wait=False):
        url = DELETE_OPS['job']
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        await self.delete(url, None, None)
        if wait:
            return await self.wait_deleted('job', namespace, name)
        return True

    async def delete_tfjob(self, namespace, name, wait=False):
        # TODO
        return None

    async def list_jobs(self, namespace):
        url = GET_OPS['list_jobs']
        params = {
            'prefix': namespace + '-'
        }
        url = url.format(
            namespace=namespace,
            endpoint=self.endpoint)
        result = await self.get(url, params)
        if result is None:
            return None
        else:
            return NomadJobList(data=result, namespace=namespace)

    async def list_tfjobs(self, namespace):
        # TODO
        return []

    async def create_job(
            self, namespace, name, image,
            command=None, args=None,
            cpu_limit=None, mem_limit=None,
            envvars={}):
        url = POST_OPS['job']
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        obj = NomadJob(
            namespace=namespace,
            name=name,
            image=image,
            command=command, args=args,
            cpu_limit=cpu_limit, mem_limit=mem_limit,
            envvars=envvars)
        obj._namespace = namespace
        obj.set_datacenters([self.datacenters])
        return await self.post(url, None, obj.payload())

    async def create_tfjob(
            self, namespace, name, image,
            command=None, args=None,
            cpu_limit=None, mem_limit=None,
            envvars={}, workers=1, ps=1,
            masters=1, tb_gs=None):
        # TODO
        return None

    async def wait_for_job(self, namespace, name):
        url = WATCH_OPS['job']
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        await self.watch(url, 'Terminated')
        job = await self.get_job(namespace, name)
        if not job.finished:
            raise Exception('Not finished')
        executions = await self.get_job_executions(namespace, name)
        return 1 if executions.is_done() else 0

    # BASIC OPS

    async def watch(self, url, value=None, timeout=20):
        not_found = True
        # TODO add timeout
        while not_found:
            allocations = await self.get(url, {})
            for alloc in allocations:
                if alloc['TaskStates'] is not None:
                    for key, values in alloc['TaskStates'].items():
                        for event in values['Events']:
                            logger.debug("Status : " + event['Type'])
                            if event['Type'] in [value]:
                                not_found = False
                                break
                if not_found is False:
                    break
            if not_found is True:
                await asyncio.sleep(5)

    async def get(self, url, params):
        async with self.session.get(
                url,
                headers={
                    'Accept': 'application/json'
                },
                params=params) as resp:
            if resp.status == 404:
                return None
            assert resp.status == 200
            result = await resp.json()
            return result

    async def post(self, url, version, payload):
        async with self.session.post(
                url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }) as resp:
            if resp.status in [201, 200]:
                return await resp.json()
            else:
                text = await resp.text()
                logger.error('Error call: %d - %s' % (resp.status, text))
                raise Exception('Error calling nomad')

    async def delete(self, url, version, payload):
        async with self.session.delete(
                url,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 404:
                return None
            else:
                text = await resp.text()
                logger.error('Error call: %d - %s' % (resp.status, text))
                raise Exception('Error calling nomad')
