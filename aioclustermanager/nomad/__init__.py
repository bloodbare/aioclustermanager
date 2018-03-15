from aioclustermanager.nomad.caller import NomadCaller

import aiohttp
import asyncio


class NomadContextManager:
    def __init__(self, environment, loop=None):
        self.environment = environment
        if loop is None:
            self.loop = asyncio.get_event_loop()
        self.session = None
        self._datacenter = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(loop=self.loop)

        url = 'http://{}/v1/agent/self'.format(self.environment['endpoint'])
        async with self.session.get(url) as resp:
            data = await resp.json()
            self._datacenter = data['config']['Datacenter']

        return NomadCaller(
            self.environment['endpoint'],
            self._datacenter,
            self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()


async def create_nomad_caller(environment):
    session = aiohttp.ClientSession()

    url = 'http://{}/v1/agent/self'.format(environment['endpoint'])
    async with session.get(url) as resp:
        data = await resp.json()
        datacenter = data['config']['Datacenter']

    return NomadCaller(
        environment['endpoint'],
        datacenter,
        session)
