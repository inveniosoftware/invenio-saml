# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that provides SAML integration.

This module is a thin layer on between Invenio and `Flask-SSO-SAML
<https://flask-sso-saml.readthedocs.io/>`_, which provides you with a set of
default handlers than can be used out of the box to authenticated users using
SSO SAML.

Handlers
--------

Flass-SSO-SAML allows you to specify handlers for each SSO action, ``sso``,
``acs``, ``slo``, ``sls`` and ``metadata``.
Typically the ones that matter the most are ``acs`` and ``sls``, because they
are the ones that will authenticate and "unauthenticate" users from the
application.

Invenio-SAML provides default handlers for ``acs`` and``sls`` actions that will
be valid for most of the use cases.
This is how you can use them (there is a more complete example on
``examples/app.py``):

.. code-block:: python

    from invenio_saml.handlers import acs_handler_factor, default_sls_handler

    def account_info(info):
        return dict(
            user=dict(
                email=info['User.email'][0],
                profile=dict(
                    username=info['User.FirstName'][0],
                    full_name=info['User.FirstName'][0])),
            external_id=info['User.email'][0],
            external_method='onelogin',
            active=True,
            confirmed_at=None)

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
                'acs_handler': acs_handler_factory(account_info),
                'sls_handler': default_sls_handler,
                'auto_confirm': False,
            }
        },

Apart from the handlers, there is one functions that needs to be specific for
each of the Identity providers, in the example before ``account_info``. This
function is responsible of extracting the user information from the SSO reponse
and transforming it so the rest of the handler understand it. You can check
more information about it on the API documentation.
"""

from __future__ import absolute_import, print_function

from .ext import InvenioSAML

__version__ = "1.0.0a3"

__all__ = ("__version__", "InvenioSAML")
