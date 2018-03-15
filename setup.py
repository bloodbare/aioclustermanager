from setuptools import find_packages, setup

import re


def load_reqs(filename):
    with open(filename) as reqs_file:
        return [
            re.sub('==', '>=', line) for line in reqs_file.readlines()
            if not re.match('\s*#', line)
        ]


version = open('VERSION').read().rstrip('\n')
requirements = load_reqs('requirements.txt')
test_requirements = load_reqs('test-requirements.txt')

try:
    README = open('README.rst').read() + '\n\n' + open('CHANGELOG.rst').read()
except IOError:
    README = None

setup(
    name='aioclustermanager',
    version=version,
    description='AsyncIO K8S and Nomad driver',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    url='http://github.com/onna/aioclustermanager',
    author='Ramon Navarro',
    author_email='ramon@onna.com',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    install_requires=requirements,
    test_suite='tests',
    tests_require=test_requirements
)
