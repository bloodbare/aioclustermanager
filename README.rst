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
