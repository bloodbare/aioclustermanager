from aioclustermanager.nomad import const
from aioclustermanager.nomad.executions_list import NomadExecutionList
from aioclustermanager.nomad.job import NomadJob
from aioclustermanager.nomad.job_list import NomadJobList
from aioclustermanager.nomad.namespace import NomadNamespace
from aioclustermanager.nomad.node_list import NomadNodeList

import asyncio
import logging

# from aioclustermanager.utils import convert

logger = logging.getLogger(__name__)

WATCH_OPS = {
    'job': 'http://{endpoint}/v1/job/{namespace}-{name}',
    'execution': 'http://{endpoint}/v1/job/{namespace}-{name}/allocations/{execution}',  # noqa
    'namespace': None
}

GET_OPS = {
    'list_jobs': 'http://{endpoint}/v1/jobs',
    'job': 'http://{endpoint}/v1/job/{namespace}-{name}',
    'executions': 'http://{endpoint}/v1/job/{namespace}-{name}/allocations',
    'log': 'http://{endpoint}/v1/client/fs/logs/{name}',
    'nodes': 'http://{endpoint}/v1/nodes'
}

POST_OPS = {
    'jobs': 'http://{endpoint}/v1/jobs',
    'job': 'http://{endpoint}/v1/job/{namespace}-{name}'
}

DELETE_OPS = {
    'job': 'http://{endpoint}/v1/job/{namespace}-{name}?purge={purge}',
    'execution': 'http://{endpoint}/v1/job/{namespace}-{name}/allocations/{execution}?purge={purge}',  # noqa
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

    async def get_nodes(self):
        url = GET_OPS['nodes']
        url = url.format(
            endpoint=self.endpoint)
        result = await self.get(url, {})
        if result is None:
            return None
        else:
            return NomadNodeList(data=result)

    async def wait_added(self, kind, namespace, name=None, timeout=30):
        url = WATCH_OPS[kind]
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        return await self.watch(url, not_value=['pending'], timeout=timeout)

    async def wait_deleted(self, kind, namespace, name=None, execution_id=None):  # noqa
        url = WATCH_OPS[kind]
        if url is None:
            return False
        url = url.format(
            namespace=namespace,
            name=name,
            execution=execution_id,
            endpoint=self.endpoint)
        return await self.watch(url, value=['dead', 'complete'])

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

    async def get_scale_deploy(self, namespace, name):
        job = await self.get_job(namespace, name)
        return job.scale

    async def set_scale_deploy(self, namespace, name, scale):
        job = await self.get_job(namespace, name)
        job.rewrap()
        url = POST_OPS['jobs']
        job.scale = scale
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        job._namespace = namespace
        return await self.post(url, None, job.payload())

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

    async def get_execution_log(self, namespace, job_id, execution_id):
        url = GET_OPS['log']
        url = url.format(
            namespace=namespace,
            name=execution_id,
            endpoint=self.endpoint)
        params = {
            'plain': 'true',
            'type': 'stdout',
            'task': namespace + '-' + job_id
        }
        result = await self.get(url, params)
        if result is None:
            return None
        else:
            return result

    async def get_execution_log_watch(self, namespace, job_id, execution_id):
        url = GET_OPS['log']
        url = url.format(
            namespace=namespace,
            name=execution_id,
            endpoint=self.endpoint)
        params = {
            'plain': 'true',
            'type': 'stdout',
            'task': namespace + '-' + job_id,
            'follow': 'true'
        }
        async for logline in await self._watch_log(url, params, timeout=3660):
            yield logline

    async def delete_job(self, namespace, name, wait=False, purge=True):
        url = DELETE_OPS['job']
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint,
            purge='true' if purge else 'false')
        await self.delete(url, None, None)
        if wait:
            return await self.wait_deleted('job', namespace, name)
        return True

    async def delete_execution(self, namespace, job_id,
                               execution_id, wait=False, purge=True):
        url = DELETE_OPS['execution']
        url = url.format(
            namespace=namespace,
            name=job_id,
            execution=execution_id,
            endpoint=self.endpoint,
            purge='true' if purge else 'false')
        await self.delete(url, None, None)
        if wait:
            return await self.wait_deleted(
                'execution', namespace, job_id, execution_id)
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
            envvars={}, volumes=None, volumeMounts=None,
            envFrom=None, entrypoint=None, **kw):
        url = POST_OPS['jobs']
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
            envvars=envvars, volumes=volumes, volumeMounts=volumeMounts,
            envFrom=envFrom, entrypoint=entrypoint, **kw)
        obj._namespace = namespace
        obj.set_datacenters([self.datacenters])
        return await self.post(url, None, obj.payload())

    async def create_tfjob(
            self, namespace, name, image,
            command=None, args=None,
            cpu_limit=None, mem_limit=None,
            envvars={}, workers=1, ps=1,
            masters=1, tb_gs=None, **kw):
        # TODO
        return None

    async def wait_for_job(self, namespace, name):
        url = WATCH_OPS['job']
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        await self.watch(url, value=['dead', 'complete'])
        job = await self.get_job(namespace, name)
        if not job.finished:
            raise Exception('Not finished')
        executions = await self.get_job_executions(namespace, name)
        return 1 if executions.is_done() else 0

    # BASIC OPS

    async def _watch_log(self, url, params, timeout=20):
        async with self.session.get(
                url,
                params=params,
                timeout=timeout) as resp:
            assert resp.status == 200
            while True:
                data = await resp.content.readline()
                yield data

    async def watch(self, url, value=None, not_value=None, timeout=30):
        return await asyncio.wait_for(
            self._watch(url, value, not_value), timeout)

    async def _watch(self, url, value=None, not_value=None):
        if value is not None and not isinstance(value, list):
            value = [value]
        if not_value is not None and not isinstance(not_value, list):
            not_value = [not_value]

        not_found = True
        while not_found:
            job = await self.get(url, {})
            if job is not None:
                if not_value is not None:
                    not_found = job['Status'] in not_value
                elif value is not None:
                    not_found = job['Status'] not in value
            if not_found is True:
                await asyncio.sleep(1)
        return job

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
                raise Exception('Error call: %d - %s' % (resp.status, text))

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
                raise Exception('Error call: %d - %s' % (resp.status, text))

    async def get_config_maps(self, namespace, labels=None):
        raise NotImplementedError()
