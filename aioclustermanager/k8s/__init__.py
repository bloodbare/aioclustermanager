from aioclustermanager.k8s.caller import K8SCaller
from base64 import b64decode

import aiohttp
import asyncio
import logging
import os
import ssl
import tempfile

logger = logging.getLogger('aioclustermanager')

SERVICE_HOST_ENV_NAME = "KUBERNETES_SERVICE_HOST"
SERVICE_PORT_ENV_NAME = "KUBERNETES_SERVICE_PORT"
SERVICE_TOKEN_ENV_NAME = "KUBERNETES_SERVICE_TOKEN"
SERVICE_TOKEN_FILENAME = "/var/run/secrets/kubernetes.io/serviceaccount/token"
SERVICE_CERT_FILENAME = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"


def _join_host_port(host, port):
    template = "%s:%s"
    host_requires_bracketing = ':' in host or '%' in host
    if host_requires_bracketing:
        template = "[%s]:%s"
    return template % (host, port)


class Configuration:
    file = None
    ssl_context = None
    cert_file = None
    scheme = 'https'

    def __init__(self, environment, loop=None):
        self.headers = {}
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

        self.environment = environment
        if environment.get('in_cluster'):
            if SERVICE_TOKEN_ENV_NAME in os.environ:
                token = os.environ[SERVICE_TOKEN_ENV_NAME]
            else:
                with open(SERVICE_TOKEN_FILENAME) as fi:
                    token = fi.read()
            self.headers = {
                'Authorization': 'Bearer ' + token
            }
            environment.update({
                'skip_ssl': True,
                'endpoint': _join_host_port(
                    os.environ[SERVICE_HOST_ENV_NAME],
                    os.environ[SERVICE_PORT_ENV_NAME])
            })

        if environment.get('certificate') is not None:
            # Certificate management
            self.load_certificate()
        elif environment.get('certificate_file') is not None:
            self.load_certificate_file()
        elif environment.get('user') and environment.get('credentials'):
            self.load_basic_auth()
        elif environment.get('skip_ssl'):
            self.load_skip_ssl()

        ssl_context = None
        if environment.get('ca') is not None:
            self.file = tempfile.NamedTemporaryFile(delete=False)
            self.file.write(bytes(environment['ca'], encoding='utf-8'))
            self.file.close()
            self.ssl_context = ssl.SSLContext()
            ssl_context.load_verify_locations(self.file.name)
        elif environment.get('ca_file') is not None:
            self.ssl_context = ssl.SSLContext()
            self.ssl_context.load_verify_locations(environment['ca_file'])

        if environment['skip_ssl']:
            self.verify = False
        else:
            self.verify = True

        if 'http_scheme' in environment:
            self.scheme = environment['http_scheme']

    def load_skip_ssl(self):
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False, loop=self.loop),
            headers=self.headers, loop=self.loop)

    def load_basic_auth(self):
        basic_auth = aiohttp.BasicAuth(
            self.environment['user'], self.environment['credentials'])
        self.session = aiohttp.ClientSession(
            auth=basic_auth, headers=self.headers, loop=self.loop)

    def load_certificate_file(self):
        logger.debug('Loading cert files')
        ssl_client_context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH)
        if 'key_file' in self.environment:
            ssl_client_context.load_cert_chain(
                certfile=self.environment['certificate_file'],
                keyfile=self.environment['key_file'])
        else:
            ssl_client_context.load_cert_chain(
                certfile=self.environment['certificate_file'])
        conn = aiohttp.TCPConnector(
            ssl_context=ssl_client_context, loop=self.loop)
        self.session = aiohttp.ClientSession(
            connector=conn, headers=self.headers, loop=self.loop)

    def load_certificate(self):
        ssl_client_context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH)
        self.cert_file = tempfile.NamedTemporaryFile(delete=False)
        self.cert_file.write(b64decode(self.environment['certificate']))
        self.cert_file.close()
        self.client_key = tempfile.NamedTemporaryFile(delete=False)
        self.client_key.write(b64decode(self.environment['key']))
        self.client_key.close()

        ssl_client_context.load_cert_chain(
            certfile=self.cert_file.name, keyfile=self.client_key.name)
        conn = aiohttp.TCPConnector(
            ssl_context=ssl_client_context, loop=self.loop)
        self.session = aiohttp.ClientSession(
            connector=conn, loop=self.loop, headers=self.headers)


class K8SContextManager:
    def __init__(self, environment, loop=None):
        self.environment = environment
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

    async def __aenter__(self):
        return await self.open()

    async def open(self):
        self.config = Configuration(self.environment, self.loop)
        return K8SCaller(
            self.config.ssl_context,
            self.environment['endpoint'],
            self.config.session,
            verify=self.config.verify,
            scheme=self.config.scheme)

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        if self.config.file is not None:
            os.unlink(self.config.file.name)
        await self.config.session.close()


async def create_k8s_caller(environment):
    config = Configuration(environment)
    return K8SCaller(
        config.ssl_context,
        environment['endpoint'],
        config.session,
        verify=config.verify,
        scheme=config.scheme)
