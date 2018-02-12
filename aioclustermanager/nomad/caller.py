import logging
import asyncio
# from aioclustermanager.utils import convert

logger = logging.getLogger(__name__)

WATCH_OPS = {
    'job': 'http://{endpoint}/v1/job/{name}/allocations'
}

GET_OPS = {
    'list_jobs': 'http://{endpoint}/v1/jobs',
    'job': 'http://{endpoint}/v1/job/{namespace}-{name}',
    'allocations': 'http://{endpoint}/v1/job/{name}/allocations'
}

PATCH_OPS = {
    'job': 'http://{endpoint}/v1/jobs/{name}'
}

PUT_OPS = {
    'job': 'http://{endpoint}/v1/jobs/{name}'
}

POST_OPS = {
    'job': 'http://{endpoint}/v1/jobs'
}

DELETE_OPS = {
    'job': 'http://{endpoint}/v1/job/{name}?purge=true'
}


K8S_TO_NOMAD = {
    'ADDED': 'Started'
}


class NomadCaller(object):
    def __init__(self, endpoint, datacenters, session):
        self.endpoint = endpoint
        self.session = session
        self.datacenters = datacenters
        self._type = 'nomad'

    @property
    def type(self):
        return self._type

    async def wait_for_done(self, namespace, name, deleted=False):
        # We need to wait the job is added check alloc for Started
        not_found = True
        while not_found:
            allocations = await self.get(namespace, 'allocations', name)
            for alloc in allocations:
                if alloc['TaskStates'] is not None:
                    for event in alloc['TaskStates'][real_job_id]['Events']:
                        if event['Type'] in ['Started']:
                            not_found = False
                            break
                if not_found is False:
                    break
            if not_found is False:
                await asyncio.sleep(5)

    async def wait_job_deleted(self, namespace, name):
        real_job_id = "%s-%s" % (namespace, name)
        # We need to wait the job is added check alloc for Started
        not_found = True
        while not_found:
            allocations = await self.get(
                real_job_id, 'allocations')
            for alloc in allocations:
                if alloc['TaskStates'] is not None:
                    for event in alloc['TaskStates'][real_job_id]['Events']:
                        if event['Type'] in ['Started']:
                            not_found = False
                            break
                if not_found is False:
                    break
            if not_found is False:
                await asyncio.sleep(5)

    async def _watch(self, namespace, name):
        allocations = await self.get(namespace, 'allocations', name)
        for alloc in allocations:
            if alloc['TaskStates'] is not None:
                for event in alloc['TaskStates'][real_job_id]['Events']:
                    if event['Type'] in ['Started']:
                        not_found = False
                        break
            if not_found is False:
                break
        await asyncio.sleep(5)

    async def watch(self, namespace, op, name=None, value=None, timeout=60):
        """
        Watch for a signal on allocations
        """
        real_job_id = "%s-%s" % (namespace, name)
        if value == 'ADDED':
            # We need to wait the job is added check alloc for Started
            not_found = True
            while not_found:
                allocations = await self._watch(namespace, name)
                for alloc in allocations:
                    if alloc['TaskStates'] is not None:
                        for event in alloc['TaskStates'][real_job_id]['Events']:
                            if event['Type'] in ['Started']:
                                not_found = False
                                break
                    if not_found is False:
                        break
                if not_found is False:
                    await asyncio.sleep(5)

    async def get(self, namespace, op, name=None):
        if op not in GET_OPS:
            return None
        url = GET_OPS[op]
        params = {}
        if op == 'list_jobs':
            params = {
                'prefix': namespace + '-'
            }
        if op == 'job':
            op = 'Job'
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
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
            return convert('nomad', result, op)

    async def patch(self, namespace, op, obj, name=None):
        if op not in PATCH_OPS:
            return None
        url = PATCH_OPS[op]
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        async with self.session.patch(
                url,
                data=obj.payload(),
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                ssl_context=self.ssl_context,
                verify_ssl=self.verify) as resp:
            assert resp.status == 200
            return await resp.json()

    async def put(self, namespace, op, obj, name=None):
        if op not in PUT_OPS:
            return None
        url = PUT_OPS[op]
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        async with self.session.put(
                url,
                data=obj.payload(),
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }) as resp:
            assert resp.status == 200
            return await resp.json()

    async def delete(self, namespace, op, obj, name=None):
        if op not in DELETE_OPS:
            return None
        url = DELETE_OPS[op]
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
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

    async def post(self, namespace, op, obj, name=None):
        if op not in POST_OPS:
            return None
        url = POST_OPS[op]
        url = url.format(
            namespace=namespace,
            name=name,
            endpoint=self.endpoint)
        obj.set_datacenters([self.datacenters])
        async with self.session.post(
                url,
                data=obj.payload(),
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
