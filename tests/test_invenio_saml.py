# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2024 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import importlib_resources as resources
import pytest
from flask import Flask
from mock import patch

from invenio_saml import InvenioSSOSAML
from invenio_saml.errors import IdentityProviderNotFound
from invenio_saml.proxies import current_sso_saml


def test_version():
    """Test version import."""
    from invenio_saml import __version__

    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask("testapp")
    ext = InvenioSSOSAML(app)
    assert "invenio-sso-saml" in app.extensions

    app = Flask("testapp")
    ext = InvenioSSOSAML()
    assert "invenio-sso-saml" not in app.extensions
    ext.init_app(app)
    assert "invenio-sso-saml" in app.extensions


def test_app_config(appctx):
    """Test app settings builder."""
    settings_idp1 = current_sso_saml.get_settings("test-idp")

    assert settings_idp1["strict"]
    assert settings_idp1["idp"]["entityId"] == "https://test-idp.com"

    # Handlers
    assert callable(current_sso_saml.get_handler("test-idp", "login_handler"))
    assert callable(current_sso_saml.get_handler("test-idp", "acs_handler"))
    assert current_sso_saml.get_handler("test-idp", "settings_handler") is None

    settings_idp2 = current_sso_saml.get_settings("idp-file")

    assert settings_idp2["idp"]["entityId"] == "https://login.idp.com"
    assert settings_idp2["sp"]["x509cert"] == "crt\n"
    assert settings_idp2["sp"]["privateKey"] == "key\n"

    with (resources.files(__name__) / "data" / "idp.xml").open() as f:
        response = f.read()

    with patch("onelogin.saml2.idp_metadata_parser.urllib2.urlopen") as urlopen_mock:
        urlopen_mock.return_value = type(
            "Response", (), {"read": lambda *args, **kwargs: response}
        )()
        settings_idp2 = current_sso_saml.get_settings("idp-url")
        assert settings_idp2["idp"]["entityId"] == "https://login.idp.com"


def test_auth(appctx, metadata_response):
    """Test Auth class."""
    with appctx.test_request_context(), pytest.raises(IdentityProviderNotFound):
        auth = current_sso_saml.get_auth("wrong-idp")

    with appctx.test_request_context():
        auth = current_sso_saml.get_auth("test-idp")
        assert auth
        assert auth.idp == "test-idp"
