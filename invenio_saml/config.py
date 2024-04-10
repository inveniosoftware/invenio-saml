# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2024 Esteban J. G. Gabancho.
#
# Flask-SSO-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Flask extension that provides SSO SAML integration."""

from invenio_saml.handlers import default_sls_handler

SSO_SAML_SESSION_KEY_NAME_ID = "SSO::SAML::NameId"
"""Key name to store the SSO Name ID in the session."""

SSO_SAML_SESSION_KEY_SESSION_INDEX = "SSO::SAML::SessionIndex"
"""Key name to store the SSO Session Index in the session."""

SSO_SAML_PREPARE_FLASK_REQUEST_FUNCTION = "invenio_saml.utils.prepare_flask_request"
"""Default function to prepare the flask request to be sent to the IdP.

If the server is behind proxys or balancers, this function might need to be
updated to use the HTTP_X_FORWARDED fields.
"""

SSO_SAML_IDPS = {}
"""SSO SAML Identity provider configuration.
This configuration variable can be used to describe the endpoints used for the
different IdPs and their settings.
The structure of the dictionary is as follows:

.. code-block:: python

    SSO_SAML_IDPS = {
        'idp-name': {
            'settings': {
                'strict': True,
                'debug': True,
                'sp': {
                    'entityId':
                    flask.url_for(
                        'sso_saml.metadata', idp='idp-name', _external=True),
                    'assertionConsumerService': {
                        'url':
                        flask.url_for(
                            'sso_saml.acs', idp='idp-name', _external=True),
                        'binding':
                        'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                    },
                    'singleLogoutService': {
                        'url':
                        flask.url_for(
                            'sso_saml.sls', idp='idp-name', _external=True),
                        'binding':
                        'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
                    },
                    'attributeConsumingService': {
                        # TODO
                    },
                    'NameIDFormat':
                    'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
                    'x509cert': '',
                    'privateKey': ''
                },
                'idp': {
                    'entityId': '',  #TODO
                    'singleSignOnService': {
                        'url': '',  # TODO
                        'binding':
                        'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                    },
                    'singleLogoutService': {
                        'url': '',  # TODO
                        'binding':
                        'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                    },
                    'x509cert': ''  # TODO oneliner
                },
                'security': {
                    'authnRequestsSigned': False,
                    'failOnAuthnContextMismatch': False,
                    'logoutRequestSigned': False,
                    'logoutResponseSigned': False,
                    'metadataCacheDuration': None,
                    'metadataValidUntil': None,
                    'nameIdEncrypted': False,
                    'requestedAuthnContext': True,
                    'requestedAuthnContextComparison': 'exact',
                    'signMetadata': False,
                    'signatureAlgorithm':
                    'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256',
                    'wantAssertionsEncrypted': False,
                    'wantAssertionsSigned': False,
                    'wantMessagesSigned': False,
                    'wantNameId': True,
                    'wantNameIdEncrypted': False,
                    'digestAlgorithm':
                    'http://www.w3.org/2001/04/xmlenc#sha256'
                },
                'contactPerson': {
                    # TODO
                },
                'organization': {
                    # TODO
                },
            },
            
            'settings_file_path': '/full/path/to/directory',
            'settings_url': 'https://...',

            "mappings": {
                "email": "TODO",
                "name": "TODO",
                "surname": "TODO",
                "external_id": "TODO",
            },

            'settings_handler': '...',
            'login_handler': '...',
            'acs_handler': acs_handler_factory('idp-name'),
            'logout_handler': '...',
            'sls_handler': '...',

            'auto_confirm': True,
        }
    }

:param settings: Setting dictionary compatible with OneLogin. Defatult values
    are show in the example. At least the following need to be provided.
    Under the Identity Provider, ``idp``, settings:
    - ``entityId``
    - ``singleSignOnService.url``
    - ``singleLogoutService.url``
    - ``x509cert``
    If you want to provide X.509cert and privateKey of the Service Provider,
    instead of via file path, you should define the following under ``sp``:
    - ``x509cert``
    - ``privateKey``
    - ``x509certNew`` (only upon certificate update)
    You might also want to provide information about ``contactPerson`` and
    ``organization`` see https://github.com/onelogin/python3-saml#settings for
    more information.
:param settings_file_path: Base folder where ``setting.json`` and
    ``advanced_settings.json`` are located. This parameter will override the
    URL parameter and update the settings found inside the configuration
    variable if any.
:param settings_url: The URL to the IdPs metadata. This parameter will update
    the values found inside the configuration variable if any.
:param settings_handler: Import path to settings handler. Python
    callable which receives two parameters, an instance of ``SAMLAuth`` and the
    current settings returned by``OneLogin_Saml2_Auth.get_settings``.
    Typically returns the settings, although it is not mandatory.
:param login_handler: Import path to login handler. Python callable which
    receives two parameters, an instance of ``SAMLAuth`` and the next url that
    the user will be redirected to. It gets called after
    ``OneLogin_Saml2_Auth.login``.
    Typically returns the next URL too, although it is not mandatory.
:param acs_handler: Import path to ACS handler. Python callable which receives
    two parameters, an instance of ``SAMLAuth`` and the next url that the user
    will be redirected to. It gets called after
    ``OneLogin_Saml2_Auth.process_response``.
    Typically returns the next URL too, although it is not mandatory.
:param logout_handler: Import path to logout handler. Python callable which
    receives two parameters, an instance of ``SAMLAuth`` and the next url that
    the user will be redirected to. It gets called after
    ``OneLogin_Saml2_Auth.logout``.
    Typically returns the next URL too, although it is not mandatory.
:param sls_handler: Import path to SLS handler. Python callable which
    receives two parameters, an instance of ``SAMLAuth`` and the next url that
    the user will be redirected to. It gets called after
    ``OneLogin_Saml2_Auth.process_slo``.
    Typically returns the next URL too, although it is not mandatory.
:param mappings: Key value pairs linking content coming from the IdP (attribute 
    response) and Invenio User properties. This key is mandatory when using the default
    acs handler in conjuction with the default account info extraction.
:param auto_confirm: Automatically set `confirmed_at` for users upon registration, 
    when using the default ``acs_handler``.
"""


# Default handlers

SSO_SAML_DEFAULT_SETTINGS_HANDLER = None
"""Default settings request handler."""

SSO_SAML_DEFAULT_LOGIN_HANDLER = None
"""Default login request handler."""

SSO_SAML_DEFAULT_ACS_HANDLER = None
"""Default ACS request handler."""

SSO_SAML_DEFAULT_LOGOUT_HANDLER = None
"""Default logout request handler."""

SSO_SAML_DEFAULT_SLS_HANDLER = default_sls_handler
"""Default SLS request handler."""

# Blueprint and routes default configuration

SSO_SAML_DEFAULT_BLUEPRINT_PREFIX = "/saml"
"""Base URL for the extensions endpoint."""

SSO_SAML_DEFAULT_METADATA_ROUTE = "/metadata/<idp>"
"""URL route for the metadata request."""

SSO_SAML_DEFAULT_SSO_ROUTE = "/sso/<idp>"
"""URL route for the SP login."""

SSO_SAML_DEFAULT_ACS_ROUTE = "/acs/<idp>"
"""URL route to handle the IdP login request."""

SSO_SAML_DEFAULT_SLO_ROUTE = "/slo/<idp>"
"""URL route for the SP logout."""

SSO_SAML_DEFAULT_SLS_ROUTE = "/sls/<idp>"
"""URL route to handle the IdP logout request."""
