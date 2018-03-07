import aiohttp
import tempfile
import ssl
import os
from base64 import b64decode
from aioclustermanager.k8s.caller import K8SCaller


class K8SContextManager(object):
    def __init__(self, environment):
        self.environment = environment
        self.session = None
        self.file = None
        self.cert_file = None
        self.client_key = None

    async def __aenter__(self):
        return await self.open()

    async def open(self):
        if self.environment['certificate'] is not None:
            # Certificate management
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
            conn = aiohttp.TCPConnector(ssl_context=ssl_client_context)
            self.session = aiohttp.ClientSession(connector=conn)
        elif self.environment['certificate_file'] is not None:
            ssl_client_context = ssl.create_default_context(
                purpose=ssl.Purpose.CLIENT_AUTH)
            ssl_client_context.load_cert_chain(
                certfile=self.environment['certificate_file'],
                keyfile=self.environment['key_file'])
            conn = aiohttp.TCPConnector(ssl_context=ssl_client_context)
            self.session = aiohttp.ClientSession(connector=conn)
        else:
            basic_auth = aiohttp.BasicAuth(
                self.environment['user'], self.environment['credentials'])
            self.session = aiohttp.ClientSession(auth=basic_auth)

        ssl_context = None
        if self.environment['ca']:
            self.file = tempfile.NamedTemporaryFile(delete=False)
            self.file.write(bytes(self.environment['ca'], encoding='utf-8'))
            self.file.close()
            ssl_context = ssl.SSLContext()
            ssl_context.load_verify_locations(self.file.name)

        if self.environment['skip_ssl']:
            verify = False
        else:
            verify = True

        return K8SCaller(
            ssl_context,
            self.environment['endpoint'],
            self.session,
            verify=verify)

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        if self.file is not None:
            os.unlink(self.file.name)
        await self.session.close()
