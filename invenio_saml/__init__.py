# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2024 Esteban J. Garcia Gabancho.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that provides SAML integration.

This module provides you with a set of default handlers than can be used out of
the box to authenticated users using SSO SAML.

Handlers
--------

Invenio-SAML allows you to specify handlers for each SSO action, ``sso``,
``acs``, ``slo``, ``sls`` and ``metadata``.
Typically the ones that matter the most are ``acs`` and ``sls``, because they
are the ones that will authenticate and "unauthenticate" users from the
application.

This module provides default handlers for ``acs`` and``sls`` actions that will
be valid for most of the use cases. The default ACS handler is created by a factory,
:func: `invenio_saml.handlers.acs_handler_function`.
This is how you can use them:

.. code-block:: python

    from invenio_saml.handlers import acs_handler_factor

    SSO_SAML_IDPS={
            '<idp-name>': {
                'settings': {
                    'idp': {
                        'entityId': '<idp-url>',
                        'singleSignOnService': {
                            'url': '<ipd-sso-url>',
                        },
                        'singleLogoutService': {
                            'url': '<idp-slo-url>',
                        },
                        'x509cert': '<ipd-cert>',
                    },
                },
                "mappings": {
                    "email": "User.email",
                    "name": "User.FirstName",
                    "surname": "User.LastName",
                    "external_id": "User.email",
                },
                'acs_handler': acs_handler_factory('<idp-name>'),
                'auto_confirm': False,
            }
        }
"""

from .ext import InvenioSSOSAML

__version__ = "1.1.0"

__all__ = ("__version__", "InvenioSSOSAML")
