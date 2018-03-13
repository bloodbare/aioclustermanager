from aioclustermanager.k8s.caller import K8SCaller
from base64 import b64decode

import aiohttp
import logging
import os
import ssl
import tempfile

logger = logging.getLogger('aioclustermanager')


class Configuration:
    file = None

    def __init__(self, environment):
        self.ssl_context = None
        self.environment = environment
        if environment['certificate'] is not None:
            # Certificate management
            ssl_client_context = ssl.create_default_context(
                purpose=ssl.Purpose.CLIENT_AUTH)
            self.cert_file = tempfile.NamedTemporaryFile(delete=False)
            self.cert_file.write(b64decode(environment['certificate']))
            self.cert_file.close()
            self.client_key = tempfile.NamedTemporaryFile(delete=False)
            self.client_key.write(b64decode(environment['key']))
            self.client_key.close()

            ssl_client_context.load_cert_chain(
                certfile=self.cert_file.name, keyfile=self.client_key.name)
            conn = aiohttp.TCPConnector(ssl_context=ssl_client_context)
            self.session = aiohttp.ClientSession(connector=conn)
        elif environment['certificate_file'] is not None:
            logger.debug('Loading cert files')
            ssl_client_context = ssl.create_default_context(
                purpose=ssl.Purpose.CLIENT_AUTH)
            ssl_client_context.load_cert_chain(
                certfile=environment['certificate_file'],
                keyfile=environment['key_file'])
            conn = aiohttp.TCPConnector(ssl_context=ssl_client_context)
            self.session = aiohttp.ClientSession(connector=conn)
        else:
            basic_auth = aiohttp.BasicAuth(
                environment['user'], environment['credentials'])
            self.session = aiohttp.ClientSession(auth=basic_auth)

        ssl_context = None
        if environment['ca'] is not None:
            self.file = tempfile.NamedTemporaryFile(delete=False)
            self.file.write(bytes(environment['ca'], encoding='utf-8'))
            self.file.close()
            self.ssl_context = ssl.SSLContext()
            ssl_context.load_verify_locations(self.file.name)
        elif environment['ca_file'] is not None:
            self.ssl_context = ssl.SSLContext()
            self.ssl_context.load_verify_locations(environment['ca_file'])

        if environment['skip_ssl']:
            self.verify = False
        else:
            self.verify = True


class K8SContextManager:
    def __init__(self, environment):
        self.environment = environment

    async def __aenter__(self):
        return await self.open()

    async def open(self):
        self.config = Configuration(self.environment)
        return K8SCaller(
            self.config.ssl_context,
            self.environment['endpoint'],
            self.config.session,
            verify=self.config.verify)

    async def __aexit__(self, exc_type, exc, tb):
        if self.config.file is not None:
            os.unlink(self.config.file.name)
        await self.config.session.close()


async def create_k8s_caller(environment):
    config = Configuration(environment)
    return K8SCaller(
        config.ssl_context,
        environment['endpoint'],
        config.session,
        verify=config.verify)
