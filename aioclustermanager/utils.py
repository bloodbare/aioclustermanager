# from aioclustermanager.job import K8SJob, NomadJob
# from aioclustermanager.job_list import K8SJobList, NomadJobList
# from aioclustermanager.allocations import NomadAllocations
import string
import random

VOWELS = "aeiou"
CONSONANTS = "".join(set(string.ascii_lowercase) - set(VOWELS))


# K8S_TYPES = {
#     'Job': K8SJob,
#     'JobList': K8SJobList,
# }

# NOMAD_TYPES = {
#     'list_jobs': NomadJobList,
#     'Job': NomadJob,
#     'allocations': NomadAllocations
# }


# def convert(kind, payload, op=None):
#     if kind == 'k8s' and op is None:
#         return K8S_TYPES[payload['kind']](data=payload)
#     elif kind == 'k8s' and op is not None:
#         return K8S_TYPES[op](data=payload)
#     else:
#         return NOMAD_TYPES[op](data=payload)


# def create_limit_obj(kind, name, max_memory, max_cpu):
#     if kind == 'k8s':
#         return K8S_TYPES['LimitRange'](
#             name=name, max_memory=max_memory, max_cpu=max_cpu)
#     elif kind == 'nomad':
#         raise NotImplementedError()


# def create_job_obj(kind, namespace, name, image, **kw):
#     if kind == 'k8s':
#         return K8S_TYPES['Job'](
#             namespace=namespace, name=name, image=image, **kw)
#     elif kind == 'nomad':
#         return NOMAD_TYPES['Job'](
#             namespace=namespace, name=name, image=image, **kw)


def generate_word(length):
    word = ""
    for i in range(length):
        if i % 2 == 0:
            word += random.choice(CONSONANTS)
        else:
            word += random.choice(VOWELS)
    return word
