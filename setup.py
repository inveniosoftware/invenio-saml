# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that provides SAML integration."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'invenio-app>=1.3.0',
    'invenio-mail>=1.0.0',
    'invenio-userprofiles>=1.0.0',
    'mock>=2.0.0',
    'redis>=2.10.5',
    'pytest-invenio>=1.4.0',
    'invenio-oauthclient>=1.5.1'
]

extras_require = {
    'docs': [
        'Sphinx>=3.3.1,<3.4',
    ],
    'mysql': [
        'invenio-db[mysql]>=1.0.9',
    ],
    'postgresql': [
        'invenio-db[postgresql]>=1.0.9',
    ],
     'sqlite': [
        'invenio-db>=1.0.9',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('mysql', 'postgresql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=3.0.0,<5',
]

install_requires = [
    'flask-sso-saml>=0.1.0',
    'invenio-accounts>=1.4.5',
    'uritools>=2.2.0',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_saml', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-saml',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio SSO SAML',
    license='MIT',
    author='Esteban J. Garcia Gabancho',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-saml',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_saml = invenio_saml:InvenioSAML',
        ],
        'invenio_base.api_apps': [
            'invenio_saml = invenio_saml:InvenioSAML',
        ],
        "invenio_base.blueprints": [
            "invenio_saml = invenio_saml.views:blueprint",
        ],
        'invenio_i18n.translations': [
            'invenio_saml = invenio_saml',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 3 - Alpha',
    ],
)
