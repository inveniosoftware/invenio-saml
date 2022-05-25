# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from __future__ import absolute_import, print_function

import pytest
from invenio_app.factory import create_app as create_invenio_app


@pytest.fixture(scope="module")
def app_config(app_config):
    """Customize application configuration."""
    app_config["APP_ALLOWED_HOSTS"] = ["localhost", "example.com"]
    # Flask-Security has ha bug in the latest release,
    # already fixed on develop branch
    app_config["SECURITY_EMAIL_SENDER"] = "no-reply@localhost"
    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return create_invenio_app


@pytest.fixture
def users(appctx, db):
    """Example users."""
    datastore = appctx.extensions["security"].datastore
    datastore.create_user(email="federico@example.com", password="tester", active=True)
    datastore.commit()
