from aioclustermanager.nomad.caller import NomadCaller

import aiohttp


class NomadContextManager:
    def __init__(self, environment):
        self.environment = environment
        self.session = None
        self._datacenter = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()

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
