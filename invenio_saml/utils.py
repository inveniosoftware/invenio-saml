# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Esteban J. G. Gabancho.
#
# Flask-SSO-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Utility functions."""

from functools import wraps
from urllib.parse import urlparse

from flask import request
from onelogin.saml2.auth import OneLogin_Saml2_Auth

from invenio_saml.proxies import current_sso_saml


def prepare_flask_request(request):
    """Prepare OneLogin-friendly request."""
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    uri_data = urlparse(request.url)
    return {
        "get_data": request.args.copy(),
        "http_host": request.host,
        "https": "on" if request.scheme == "https" else "off",
        "post_data": request.form.copy(),
        "script_name": request.path,
        "server_port": uri_data.port,
        # Uncomment if using ADFS as IdP,
        # https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
    }


def run_handler(handler_name):
    """Find a handler inside configuration and call it."""

    def decorated(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            res = f(self, *args, **kwargs)
            handler = current_sso_saml.get_handler(self.idp, handler_name)
            if handler:
                return handler(self, res)
            return res

        return inner

    return decorated


class SAMLAuth(OneLogin_Saml2_Auth):
    """Encapsulate OneLogin SP SAML instance."""

    def __init__(self, idp, settings, *args, **kwargs):
        """Initialization."""
        self.idp = idp
        self._settings = settings
        req = current_sso_saml.prepare_flask_request(request)
        super(SAMLAuth, self).__init__(req, self._settings, *args, **kwargs)

    @run_handler("settings_handler")
    def get_settings(self):
        """Get settings info and call handler.

        :return: ``OneLogin_Saml2_Setting`` object
        """
        settings = super(SAMLAuth, self).get_settings()
        return settings

    @run_handler("login_handler")
    def login(self, *args, **kwargs):
        """Wrapper around ``OneLogin_Saml2_Auth.login``."""
        next_url = super(SAMLAuth, self).login(*args, **kwargs)
        return next_url

    @run_handler("logout_handler")
    def logout(self, *args, **kwargs):
        """Wrapper around ``OneLogin_Saml2_Auth.logout``."""
        next_url = super(SAMLAuth, self).logout(*args, **kwargs)
        return next_url

    @run_handler("acs_handler")
    def acs_handler(self, next_url):
        """Call ACS handler from config."""
        return next_url

    @run_handler("sls_handler")
    def sls_handler(self, next_url):
        """Call SLS handler from config."""
        return next_url
