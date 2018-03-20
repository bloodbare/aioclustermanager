from aioclustermanager.k8s import K8SContextManager
from aioclustermanager.manager import ClusterManager
from aioclustermanager.nomad import NomadContextManager
from aioclustermanager.tests.utils import get_k8s_config

import os
import pytest


@pytest.fixture(scope='function')
async def k8s_config():
    return get_k8s_config()


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
