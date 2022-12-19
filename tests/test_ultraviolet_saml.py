# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

from flask import Flask

from ultraviolet_saml import UltravioletSAML


def test_version():
    """Test version import."""
    from ultraviolet_saml import __version__

    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask("testapp")
    ext = UltravioletSAML(app)
    assert "ultraviolet-saml" in app.extensions

    app = Flask("testapp")
    ext = UltravioletSAML()
    assert "ultraviolet-saml" not in app.extensions
    ext.init_app(app)
    assert "ultraviolet-saml" in app.extensions
