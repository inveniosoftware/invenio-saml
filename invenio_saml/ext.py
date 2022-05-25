# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that provides SAML integration."""

from __future__ import absolute_import, print_function

from flask_sso_saml import FlaskSSOSAML

from . import config


class InvenioSAML(object):
    """Invenio-SAML extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        if "flask-sso-saml" not in app.extensions:
            FlaskSSOSAML(app)
        app.extensions["invenio-saml"] = self
