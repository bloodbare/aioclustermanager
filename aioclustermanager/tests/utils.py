from pathlib import Path

import os
import yaml


def get_k8s_config():
    home = str(Path.home())
    # Designed to run on docker desktop k8s support
    # XXX DOES NOT CURRENTLY WORK WITH containers running in k8s already
    if os.environ.get('TEST_INSIDE_K8S', False):
        config_k8s = {
            'in_cluster': True
        }
        return config_k8s

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
