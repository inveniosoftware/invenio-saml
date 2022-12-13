# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Esteban J. G. Gabancho.
#
# Flask-SSO-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Proxy objects for easier access to application objects."""

from flask import current_app
from werkzeug.local import LocalProxy


def _get_current_sso_saml():
    """Return current state of the SSO SAML extension."""
    return current_app.extensions["invenio-sso-saml"]


current_sso_saml = LocalProxy(_get_current_sso_saml)
