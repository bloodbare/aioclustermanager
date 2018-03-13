from aioclustermanager.k8s import K8SContextManager
from aioclustermanager.manager import ClusterManager
from aioclustermanager.nomad import NomadContextManager
from pathlib import Path

import os
import pytest
import yaml


@pytest.fixture(scope='function')
async def k8s_config():
    home = str(Path.home())
    # Designed to run on docker desktop k8s support
    # XXX DOES NOT CURRENTLY WORK WITH containers running in k8s already
    with open(home + '/.kube/config', 'r') as f:
        configuration = yaml.load(f)

    CERT_DOCKER = None
    KEY_DOCKER = None
    CERT_DOCKER_FILE = None
    KEY_DOCKER_FILE = None
    K8S_CA = None
    K8S_CA_FILE = None
    K8S_USER = None
    K8S_PASSWORD = None
    K8S_SKIP_SSL = True
    K8S_ENDPOINT = 'localhost:6443'
    TRAVIS = os.environ.get('TRAVIS', 'false')
    # Looking for docker-for-desktop or minikube
    defined = False
    for user in configuration['users']:
        if user['name'] == 'docker-for-desktop':
            CERT_DOCKER = user['user']['client-certificate-data']
            KEY_DOCKER = user['user']['client-key-data']
            defined = True
        if user['name'] == 'minikube' and defined is False and TRAVIS != 'true':  # noqa
            CERT_DOCKER_FILE = user['user']['client-certificate']
            KEY_DOCKER_FILE = user['user']['client-key']
        if TRAVIS == 'true':
            K8S_USER = 'testinguser'
            K8S_PASSWORD = '12345678'
    for cluster in configuration['clusters']:
        if cluster['name'] == 'minikube' and defined is False:
            K8S_SKIP_SSL = False
            K8S_ENDPOINT = cluster['cluster']['server']
            K8S_ENDPOINT = K8S_ENDPOINT.replace("https://", "")
            K8S_CA_FILE = cluster['cluster']['certificate-authority']

    config_k8s = {
        'user': os.environ.get('TEST_K8S_USER', K8S_USER),
        'credentials': os.environ.get('TEST_K8S_CREDS', K8S_PASSWORD),
        'ca': os.environ.get('TEST_K8S_CA', K8S_CA),
        'ca_file': os.environ.get('TEST_K8S_CA_FILE', K8S_CA_FILE),
        'endpoint': os.environ.get('TEST_K8S_ENDPOINT', K8S_ENDPOINT),
        'skip_ssl': K8S_SKIP_SSL,
        'certificate': os.environ.get('TEST_K8S_CERT', CERT_DOCKER),
        'key': os.environ.get('TEST_K8S_KEY', KEY_DOCKER),
        'certificate_file': os.environ.get('TEST_K8S_CERT_FILE', CERT_DOCKER_FILE),  # noqa
        'key_file': os.environ.get('TEST_K8S_KEY_FILE', KEY_DOCKER_FILE)
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
        # XXX context managers here feel very clumsy
        # In another app, I have a single instance of a cluster manager
        # that runs forever. Needing the configuration of the manager to
        # be in a context manager makes this clumsy.
        # see changes in the __init__.py for another approach
        cm = ClusterManager(context)
        await cm.delete_namespace('aiocluster-test')
        await cm.create_namespace('aiocluster-test')
        yield cm
        await cm.delete_namespace('aiocluster-test')


@pytest.fixture(scope='function')
async def nomad(nomad_config):

    async with NomadContextManager(nomad_config) as context:
        # XXX context managers here feel very clumsy
        cm = ClusterManager(context)
        await cm.delete_namespace('aiocluster-test')
        await cm.create_namespace('aiocluster-test')
        yield cm
        await cm.delete_namespace('aiocluster-test')
