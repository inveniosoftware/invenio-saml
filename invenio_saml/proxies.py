# SPDX-FileCopyrightText: 2022 Esteban J. G. Gabancho.
# SPDX-License-Identifier: MIT

"""Proxy objects for easier access to application objects."""

from flask import current_app
from werkzeug.local import LocalProxy


def _get_current_sso_saml():
    """Return current state of the SSO SAML extension."""
    return current_app.extensions["invenio-sso-saml"]


current_sso_saml = LocalProxy(_get_current_sso_saml)
