import pytest
import os
import yaml
from aioclustermanager.k8s import K8SContextManager
from aioclustermanager.nomad import NomadContextManager
from aioclustermanager.manager import ClusterManager
from pathlib import Path


@pytest.fixture(scope='function')
async def k8s_config():
    home = str(Path.home())
    # Designed to run on docker desktop k8s support
    with open(home + '/.kube/config', 'r') as f:
        configuration = yaml.load(f)

    CERT_DOCKER = None
    # Looking for docker-for-desktop
    for user in configuration['users']:
        if user['name'] == 'docker-for-desktop':
            CERT_DOCKER = user['user']['client-certificate-data']
            KEY_DOCKER = user['user']['client-key-data']

    config_k8s = {
        'user': os.environ.get('TEST_K8S_USER', None),
        'credentials': os.environ.get('TEST_K8S_CREDS', None),
        'ca': os.environ.get('TEST_K8S_CA', None),
        'endpoint': os.environ.get('TEST_K8S_ENDPOINT', 'localhost:6443'),
        'skip_ssl': True,
        'certificate': os.environ.get('TEST_K8S_CERT', CERT_DOCKER),
        'key': os.environ.get('TEST_K8S_KEY', KEY_DOCKER)
    }
    return config_k8s


@pytest.fixture(scope='function')
async def nomad_config():
    config_nomad = {
        'endpoint': os.environ.get('TEST_NOMAD_ENDPOINT', 'localhost:4646')
    }
    return config_nomad


@pytest.fixture(scope='function')
async def kubernetes(k8s_config):

    async with K8SContextManager(k8s_config) as context:
        cm = ClusterManager(context)
        await cm.delete_namespace('aiocluster-test')
        await cm.create_namespace('aiocluster-test')
        yield cm
        await cm.delete_namespace('aiocluster-test')


@pytest.fixture(scope='function')
async def nomad(nomad_config):

    async with NomadContextManager(nomad_config) as context:
        cm = ClusterManager(context)
        await cm.delete_namespace('aiocluster-test')
        await cm.create_namespace('aiocluster-test')
        yield cm
        await cm.delete_namespace('aiocluster-test')
