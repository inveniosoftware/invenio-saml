# -*- coding: utf-8 -*-
#
# Copyright (C) 2019, 2022 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that provides SAML integration."""

import json
from collections.abc import Mapping
from functools import wraps

from flask import url_for
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser
from werkzeug.utils import cached_property, import_string

from . import config
from .errors import IdentityProviderNotFound
from .utils import SAMLAuth, prepare_flask_request
from .views import create_blueprint


def _default_config(idp):
    """Default IdP configuration."""
    return dict(
        settings={
            "strict": True,
            "debug": True,
            "sp": {
                "entityId": url_for("sso_saml.metadata", idp=idp, _external=True),
                "assertionConsumerService": {
                    "url": url_for("sso_saml.acs", idp=idp, _external=True),
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                },
                "singleLogoutService": {
                    "url": url_for("sso_saml.sls", idp=idp, _external=True),
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                },
                "NameIDFormat": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                "x509cert": "",
                "privateKey": "",
            },
            "idp": {
                "entityId": None,
                "singleSignOnService": {
                    "url": None,
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                },
                "singleLogoutService": {
                    "url": None,
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                },
                "x509cert": None,
            },
            "security": {
                "authnRequestsSigned": False,
                "failOnAuthnContextMismatch": False,
                "logoutRequestSigned": False,
                "logoutResponseSigned": False,
                "metadataCacheDuration": None,
                "metadataValidUntil": None,
                "nameIdEncrypted": False,
                "requestedAuthnContext": True,
                "requestedAuthnContextComparison": "exact",
                "signMetadata": False,
                "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
                "wantAssertionsEncrypted": False,
                "wantAssertionsSigned": False,
                "wantMessagesSigned": False,
                "wantNameId": True,
                "wantNameIdEncrypted": False,
                "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
            },
        },
        settings_file_path=None,
        settings_url=None,
        sp_cert_file=None,
        sp_key_file=None,
        settings_handler=None,
        login_handler=None,
        acs_handler=None,
        logout_handler=None,
        sls_handler=None,
    )


def _cached_configuration(f):
    """Cache the IdP configuration for future use."""

    @wraps(f)
    def inner(self, idp, *args, **kwargs):
        if idp not in self._saml_config:
            try:
                self._saml_config[idp] = self._build_configuration(idp)
            except KeyError as exc:
                raise IdentityProviderNotFound() from exc
        return f(self, idp, *args, **kwargs)

    return inner


class _InvenioSSOSAMLState(object):
    """Invenio SSO SAML state object."""

    def __init__(self, app):
        """Initialize state."""
        self.app = app
        self._saml_config = {}

    @property
    def url_prefix(self):
        """URL prefix from config."""
        return self.app.config["SSO_SAML_DEFAULT_BLUEPRINT_PREFIX"]

    @property
    def metadata_url(self):
        """SSO metadata URL from config."""
        return self.app.config["SSO_SAML_DEFAULT_METADATA_ROUTE"]

    @property
    def sso_url(self):
        """SSO SSO URL from config."""
        return self.app.config["SSO_SAML_DEFAULT_SSO_ROUTE"]

    @property
    def acs_url(self):
        """SSO ACS URL from config."""
        return self.app.config["SSO_SAML_DEFAULT_ACS_ROUTE"]

    @property
    def slo_url(self):
        """SSO SLO URL from config."""
        return self.app.config["SSO_SAML_DEFAULT_SLO_ROUTE"]

    @property
    def sls_url(self):
        """SSO SLS URL from config."""
        return self.app.config["SSO_SAML_DEFAULT_SLS_ROUTE"]

    @cached_property
    def prepare_flask_request(self):
        """Function to prepare flask request for OneLogin."""
        prep_func = self.app.config["SSO_SAML_PREPARE_FLASK_REQUEST_FUNCTION"]
        if isinstance(prep_func, str):
            prep_func = import_string(prep_func)
        return prep_func

    @_cached_configuration
    def get_settings(self, idp):
        """Find settings for a particular Identity Provider."""
        return self._saml_config[idp]["settings"]

    @_cached_configuration
    def get_handler(self, idp, handler):
        """Get handler for idp."""
        return self._saml_config[idp][handler]

    def get_auth(self, idp):
        """Instantiate the IdP."""
        return SAMLAuth(idp, self.get_settings(idp))

    def _build_configuration(self, idp):
        """Update default config with the ones read from configuration."""

        def update(d, u):
            for k, v in u.items():
                if isinstance(v, Mapping):
                    d[k] = update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d

        def make_handler(handler, default=None):
            handler = handler if handler else default
            return (
                import_string(handler)
                if handler and isinstance(handler, str)
                else handler
            )

        config = _default_config(idp)
        update(config, self.app.config["SSO_SAML_IDPS"][idp])

        # Read IdP config from file or URL if any
        if config["settings_url"]:
            external_conf = OneLogin_Saml2_IdPMetadataParser.parse_remote(
                config["settings_url"]
            )
            config["settings"]["idp"].update(external_conf.get("idp"))

        if config["settings_file_path"]:
            with open(config["settings_file_path"], "r") as idp:
                file = config["settings_file_path"]
                # xml format
                if file.endswith(".xml"):
                    external_conf = OneLogin_Saml2_IdPMetadataParser.parse(idp.read())
                # json format
                elif file.endswith(".json"):
                    external_conf = json.loads(idp.read())
            config["settings"]["idp"].update(external_conf.get("idp"))

        # Load certificate and key
        if config["sp_cert_file"]:
            with open(config["sp_cert_file"], "r") as cf:
                cert = cf.read()
            config["settings"]["sp"]["x509cert"] = cert

        if config["sp_key_file"]:
            with open(config["sp_key_file"], "r") as cf:
                cert = cf.read()
            config["settings"]["sp"]["privateKey"] = cert

        # Import handlers is present
        config["settings_handler"] = make_handler(
            config["settings_handler"],
            self.app.config.get("SSO_SAML_DEFAULT_SETTINGS_HANDLER"),
        )
        config["login_handler"] = make_handler(
            config["login_handler"],
            self.app.config.get("SSO_SAML_DEFAULT_LOGIN_HANDLER"),
        )
        config["logout_handler"] = make_handler(
            config["logout_handler"],
            self.app.config.get("SSO_SAML_DEFAULT_LOGOUT_HANDLER"),
        )
        config["acs_handler"] = make_handler(
            config["acs_handler"],
            self.app.config.get("SSO_SAML_DEFAULT_ACS_HANDLER"),
        )
        config["sls_handler"] = make_handler(
            config["sls_handler"],
            self.app.config.get("SSO_SAML_DEFAULT_SLS_HANDLER"),
        )

        return config


class InvenioSSOSAML(object):
    """Invenio-SSO-SAML extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        state = _InvenioSSOSAMLState(app)

        # Register blueprint and routes
        app.register_blueprint(create_blueprint(state, __name__))

        app.extensions["invenio-sso-saml"] = state
        return state

    def init_config(self, app):
        """Initialize configuration."""
        # Only load the configuration, we'll build it lazily because we can
        for k in dir(config):
            if k.startswith("SSO_SAML_"):
                app.config.setdefault(k, getattr(config, k))

        # Set default when needed
        app.config.setdefault(
            "SSO_SAML_PREPARE_FLASK_REQUEST_FUNCTION", prepare_flask_request
        )
