# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Esteban J. G. Gabancho.
#
# Flask-SSO-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Views tests."""

import pytest
from flask import url_for
from flask_security import url_for_security
from mock import patch


def test_wrong_idp(appctx, base_client):
    """Test wrong Identity Provider name."""
    client = base_client
    login_url = url_for("sso_saml.sso", idp="wrong-idp")
    res = client.get(login_url)
    assert res.status_code == 404


def test_login_error(appctx, base_client):
    """Test login error."""
    client = base_client
    login_url = url_for("sso_saml.sso", idp="test-idp")
    with patch("invenio_saml.utils.SAMLAuth.login") as mock_login:
        mock_login.return_value = None
        res = client.get(login_url)
        assert res.status_code == 401


def test_login(appctx, base_client):
    """Test SSO requests."""
    client = base_client
    login_url = url_for("sso_saml.sso", idp="test-idp")
    res = client.get(login_url)
    assert res.status_code == 302
    assert res.location.startswith("https://test-ipd.com/sso?")

    login_url = url_for("sso_saml.sso", idp="test-idp", next="/next_url")
    res = client.get(login_url)
    assert res.status_code == 302
    assert res.location.startswith("https://test-ipd.com/sso?")
    assert "RelayState=%2Fnext_url" in res.location


@pytest.mark.freeze_time("2019-04-19T13:35:47Z")
def test_acs(appctx, base_client, sso_response):
    """Test ACS request."""
    client = base_client
    acs_url = url_for("sso_saml.acs", idp="test-idp")

    res = client.post(acs_url, data=dict(SAMLResponse=""))
    assert res.status_code == 400

    res = client.post(acs_url, data=dict(SAMLResponse=sso_response))
    assert res.status_code == 401

    with patch(
        "onelogin.saml2.auth.OneLogin_Saml2_Response.is_valid"
    ) as mock_is_valid, patch(
        "invenio_saml.utils.SAMLAuth.is_authenticated"
    ) as mock_is_authenticated:
        mock_is_valid.return_value = True
        mock_is_authenticated.return_value = False
        res = client.post(acs_url, data=dict(SAMLResponse=sso_response))
        assert res.status_code == 403

    with patch("onelogin.saml2.auth.OneLogin_Saml2_Response.is_valid") as mock_is_valid:
        mock_is_valid.return_value = True
        res = client.post(acs_url, data=dict(SAMLResponse=sso_response))
        assert res.status_code == 302


def test_logout(appctx, base_client):
    """Test SLO requests."""
    client = base_client
    logout_url = url_for("sso_saml.slo", idp="test-idp")
    with client.session_transaction() as sess:
        sess["SSO::SAML::NameId"] = "ID"
        sess["SSO::SAML::SessionIndex"] = "INDEX"
    res = client.get(logout_url)
    assert res.status_code == 302
    assert res.location.startswith("https://test-ipd.com/slo?")


def test_logout_error(appctx, base_client):
    """Test logout error."""
    client = base_client
    login_url = url_for("sso_saml.slo", idp="test-idp")
    with patch("invenio_saml.utils.SAMLAuth.logout") as mock_logout:
        mock_logout.return_value = None
        res = client.get(login_url)
        assert res.status_code == 401


def test_sls(appctx, base_client, slo_query_string):
    """Test SLS request."""
    client = base_client
    sls_url = url_for("sso_saml.sls", idp="test-idp")
    res = client.get(sls_url, query_string=slo_query_string)
    assert res.status_code == 302

    with patch("invenio_saml.utils.SAMLAuth.get_errors") as mock_get_erros, patch(
        "invenio_saml.utils.SAMLAuth.get_last_error_reason"
    ) as mock_get_reason:
        mock_get_erros.return_value = ["bad error"]
        mock_get_reason.return_value = "Test reason"
        res = client.get(sls_url, query_string=slo_query_string)
        assert res.status_code == 401
        assert res.json == ["bad error", "Test reason"]


@pytest.mark.freeze_time("2019-04-18")
def test_metadata(appctx, base_client, metadata_response):
    """Test metadata request."""
    client = base_client
    metadata_url = url_for("sso_saml.metadata", idp="test-idp")
    res = client.get(metadata_url)
    assert res.status_code == 200
    assert res.data == metadata_response

    with patch(
        "onelogin.saml2.settings.OneLogin_Saml2_Settings.validate_metadata"
    ) as mock_validate_metadata, patch(
        "invenio_saml.utils.SAMLAuth.get_last_error_reason"
    ) as mock_get_reason:
        mock_validate_metadata.return_value = ["bad error", "worst error"]
        mock_get_reason.return_value = "Test reason"
        res = client.get(metadata_url)
        assert res.status_code == 401
        assert res.json == ["bad error", "worst error", "Test reason"]


def test_login_template(appctx, base_client):
    """Test the SAML login template at least loads."""
    client = base_client
    res = client.get(url_for_security("login"))
    assert res.status_code == 200
    assert "Sign in with SAML" in res.text
