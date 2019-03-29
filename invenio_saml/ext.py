# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that provides SAML integration."""

from __future__ import absolute_import, print_function

from flask_babelex import gettext as _

from . import config


class InvenioSAML(object):
    """Invenio-SAML extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        # TODO: This is an example of translation string with comment. Please
        # remove it.
        # NOTE: This is a note to a translator.
        _('A translation string')
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['invenio-saml'] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Use theme's base template if theme is installed
        if 'BASE_TEMPLATE' in app.config:
            app.config.setdefault(
                'SAML_BASE_TEMPLATE',
                app.config['BASE_TEMPLATE'],
            )
        for k in dir(config):
            if k.startswith('SAML_'):
                app.config.setdefault(k, getattr(config, k))
