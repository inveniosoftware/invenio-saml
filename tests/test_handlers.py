# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2024 Esteban J. Garcia Gabancho.
# Copyright (C) 2021-2022 Graz University of Technology.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Test handlers."""

from datetime import datetime, timezone

import pytest
from flask import current_app
from flask_security import current_user, login_user
from invenio_accounts.models import User
from invenio_accounts.proxies import current_datastore
from invenio_oauthclient.models import UserIdentity
from mock import Mock, patch
from werkzeug.exceptions import Unauthorized

from invenio_saml.handlers import (
    acs_handler_factory,
    default_account_setup,
    default_sls_handler,
)


def test_default_account_setup(users):
    """Test default user account setup."""
    user = User.query.filter_by(email="federico@example.com").one()
    account_info = dict(
        external_id="123456",
        external_method="external",
        other="foo",
    )

    default_account_setup(user, account_info)

    identities = UserIdentity.query.filter_by(id_user=user.id).all()
    assert len(identities) == 1
    assert identities[0].user == user

    # If we do it again there is still one row only
    default_account_setup(user, account_info)
    identities = UserIdentity.query.filter_by(id_user=user.id).all()
    assert len(identities) == 1
    assert identities[0].user == user


def test_default_sls_handler(appctx, users):
    """Test default SLS handler."""
    with appctx.test_request_context():
        user = User.query.filter_by(email="federico@example.com").one()
        login_user(user)
        assert current_user.is_authenticated
        # call the SLS handler
        next_url = default_sls_handler(None, "/foo")
        assert not current_user.is_authenticated
        assert next_url == "/foo"


def test_acs_handler_factory(appctx, db):
    """Test ACS handler factory."""
    appctx.config["SSO_SAML_IDPS"] = {
        "test": {
            "mappings": {
                "email": "email",
                "name": "name",
                "surname": "surname",
                "external_id": "external_id",
            },
        }
    }
    attrs = dict(
        email=["federico@example.com"],
        name=["federico"],
        surname=["Fernandez"],
        external_id=["12345679abcdf"],
    )

    acs_handler = acs_handler_factory("test")

    with appctx.test_request_context(), patch(
        "invenio_saml.utils.SAMLAuth"
    ) as mock_saml_auth:
        mock_saml_auth.get_attributes.return_value = attrs
        next_url = acs_handler(mock_saml_auth, "/foo")

        assert next_url == "/foo"
        assert current_user.is_authenticated
        assert current_user.confirmed_at is None


def test_acs_handler_factory_config(appctx, db):
    """Test ACS handler factory with config."""

    appctx.config["SSO_SAML_IDPS"] = {
        "test": {
            "mappings": {
                "email": "email",
                "name": "name",
                "surname": "surname",
                "external_id": "external_id",
            },
            "auto_confirm": True,
        }
    }
    attrs = dict(
        email=["federico@example.com"],
        name=["federico"],
        surname=["Fernandez"],
        external_id=["12345679abcdf"],
    )

    acs_handler = acs_handler_factory("test")

    with appctx.test_request_context(), patch(
        "invenio_saml.utils.SAMLAuth"
    ) as mock_saml_auth:
        mock_saml_auth.get_attributes.return_value = attrs
        acs_handler(mock_saml_auth, "/foo")

        assert current_user.is_authenticated
        assert current_user.confirmed_at


def test_acs_handler_authetication_error(appctx, db):
    """Test ACS handler factory authentication errors."""
    attrs = dict(
        email=["federico@example.com"],
        name=["federico"],
        surname=["Fernandez"],
        external_id=["12345679abcdf"],
    )

    acs_handler = acs_handler_factory("test")

    with appctx.test_request_context(), patch(
        "invenio_saml.utils.SAMLAuth"
    ) as mock_saml_auth, patch(
        "invenio_saml.handlers.account_authenticate"
    ) as mock_authenticate:
        mock_saml_auth.get_attributes.return_value = attrs
        mock_authenticate.return_value = False
        with pytest.raises(Unauthorized):
            acs_handler(mock_saml_auth, "/foo")


def test_acs_handler_user_creation_error(appctx, db):
    """Test ACS handler factory user creation errors."""
    attrs = dict(
        email=["federico@example.com"],
        name=["federico"],
        surname=["Fernandez"],
        external_id=["12345679abcdf"],
    )

    acs_handler = acs_handler_factory("test")

    with appctx.test_request_context(), patch(
        "invenio_saml.utils.SAMLAuth"
    ) as mock_saml_auth, patch(
        "invenio_saml.handlers.account_register"
    ) as mock_register:
        mock_saml_auth.get_attributes.return_value = attrs
        mock_register.return_value = None
        with pytest.raises(Unauthorized):
            acs_handler(mock_saml_auth, "/foo")


def test_custom_account_info(appctx, db):
    """Test custom account info in ACS handler."""
    appctx.config["SSO_SAML_IDPS"] = {
        "test": {
            "auto_confirm": True,
        }
    }

    def account_info(attributes, remote_app):
        remote_app_config = current_app.config["SSO_SAML_IDPS"].get(remote_app, {})
        return dict(
            user=dict(
                email=attributes["email"],
                profile=dict(
                    username=attributes["name"],
                    full_name=f"{attributes['name']} {attributes['surname']}",
                ),
            ),
            external_id=f"{attributes['name']}.{attributes['surname']}",
            external_method=remote_app,
            active=True,
            confirmed_at=(
                datetime.now(timezone.utc)
                if remote_app_config.get("auto_confirm", False)
                else None
            ),
        )

    attrs = dict(
        email="federico@example.com",
        name="federico",
        surname="fernandez",
    )

    acs_handler = acs_handler_factory("test", account_info=account_info)

    with appctx.test_request_context(), patch(
        "invenio_saml.utils.SAMLAuth"
    ) as mock_saml_auth:
        mock_saml_auth.get_attributes.return_value = attrs
        acs_handler(mock_saml_auth, "/")

        assert current_user.is_authenticated
        assert current_user.confirmed_at


def test_custom_user_lookup(appctx, users):
    """Test custom user lookup in ACS handler."""
    appctx.config["SSO_SAML_IDPS"] = {
        "test": {
            "mappings": {
                "email": "email",
                "name": "name",
                "surname": "surname",
                "external_id": "external_id",
            },
        }
    }
    attrs = dict(
        email=["federico@example.com"],
        name=["federico"],
        surname=["Fernandez"],
        external_id=["12345679abcdf"],
    )

    user = current_datastore.get_user_by_email("federico@example.com")

    mock_user_lookup = Mock(return_value=user)

    acs_handler = acs_handler_factory("test", user_lookup=mock_user_lookup)

    with appctx.test_request_context(), patch(
        "invenio_saml.utils.SAMLAuth"
    ) as mock_saml_auth:
        mock_saml_auth.get_attributes.return_value = attrs
        acs_handler(mock_saml_auth, "/")

        assert mock_user_lookup.call_count == 1
        assert current_user.is_authenticated
        assert current_user.confirmed_at is None
