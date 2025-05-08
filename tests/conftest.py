# -*- coding: utf-8 -*-
#
# Copyright (C) 2019, 2022 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import base64
from urllib.parse import urlencode

import importlib_resources as resources
import pytest
from flask_webpackext.manifest import (
    JinjaManifest,
    JinjaManifestEntry,
    JinjaManifestLoader,
)
from invenio_app.factory import create_app as create_invenio_app
from onelogin.saml2.utils import OneLogin_Saml2_Utils as saml_utils


#
# Mock the webpack manifest to avoid having to compile the full assets.
#
class MockJinjaManifest(JinjaManifest):
    """Mock manifest."""

    def __getitem__(self, key):
        """Get a manifest entry."""
        return JinjaManifestEntry(key, [key])

    def __getattr__(self, name):
        """Get a manifest entry."""
        return JinjaManifestEntry(name, [name])


class MockManifestLoader(JinjaManifestLoader):
    """Manifest loader creating a mocked manifest."""

    def load(self, filepath):
        """Load the manifest."""
        return MockJinjaManifest()


@pytest.fixture(scope="module")
def app_config(app_config):
    """Customize application configuration."""
    app_config["APP_ALLOWED_HOSTS"] = [
        "localhost",
        "example.com",
        "tests.com:5000",
    ]
    # Flask-Security has ha bug in the latest release,
    # already fixed on develop branch
    app_config["SECURITY_EMAIL_SENDER"] = "no-reply@localhost"
    app_config["WEBPACKEXT_MANIFEST_LOADER"] = MockManifestLoader
    app_config["SERVER_NAME"] = "localhost"
    app_config["SSO_SAML_DEFAULT_LOGIN_HANDLER"] = lambda auth, next_url: next_url
    app_config["SSO_SAML_IDPS"] = {
        "test-idp": {
            "settings": {
                "idp": {
                    "entityId": "https://test-idp.com",
                    "singleSignOnService": {
                        "url": "https://test-ipd.com/sso",
                    },
                    "singleLogoutService": {
                        "url": "https://test-ipd.com/slo",
                    },
                    "x509cert": "cert",
                }
            },
            "acs_handler": lambda auth, next_url: next_url,
        },
        "idp-file": {
            "settings_file_path": str(resources.files(__name__) / "data" / "idp.xml"),
            "sp_cert_file": str(resources.files(__name__) / "data" / "cert.crt"),
            "sp_key_file": str(resources.files(__name__) / "data" / "cert.key"),
        },
        "idp-url": {"settings_url": "https://test-idp.com/settings"},
    }
    # Add template
    app_config["OAUTHCLIENT_LOGIN_USER_TEMPLATE"] = "invenio_saml/login_user.html"
    app_config["THEME_FRONTPAGE"] = False
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


@pytest.fixture(scope="module")
def sso_response():
    """Mock SSO response from Identity Provider."""
    with (resources.files(__name__) / "data" / "sso_response.xml").open("rb") as f:
        return base64.b64encode(f.read())


@pytest.fixture(scope="module")
def slo_query_string():
    """Mock SLO response from Identity Provider."""
    with (resources.files(__name__) / "data" / "slo_response.xml").open() as f:
        slo_response = saml_utils.deflate_and_base64_encode(f.read())
    return urlencode(dict(SAMLResponse=slo_response))


@pytest.fixture(scope="module")
def metadata_response():
    """Metadata response."""
    with (resources.files(__name__) / "data" / "metadata.xml").open("rb") as f:
        return f.read()
