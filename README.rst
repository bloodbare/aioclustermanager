Introduction
============

An asyncio library to manage orchestrators with support for Kubernetes and Nomad.


Quickstart
----------

We use context managers with a configuration object::

    config_k8s = {
        'certificate': '<client certificate data>',
        'key': '<client key data>',
        'endpoint': 'localhost:6443',
        'skip_ssl': True
    }
    async with K8SContextManager(k8s_config) as context:
          cm = ClusterManager(context)
          await cm.delete_namespace('aiocluster-test')
          await cm.create_namespace('aiocluster-test')

To Run Tests
------------

Nomad:

You can download the nomad agent and run it with:

    nomad agent -dev

Tests will connect to the local nomad to schedule the jobs

K8S:

Tests will check if there is a k8s context names docker-for-desktop or minikube