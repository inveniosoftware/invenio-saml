# -*- coding: utf-8 -*-
#
# Copyright (C)      2019 Esteban J. Garcia Gabancho.
# Copyright (C) 2021-2022 Graz University of Technology.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Test handlers."""

import pytest
from flask_security import current_user, login_user
from invenio_accounts.models import User
from invenio_db import db
from invenio_oauthclient.models import UserIdentity
from mock import patch
from werkzeug.exceptions import Unauthorized

from invenio_saml.handlers import (
    acs_handler_factory,
    default_account_setup,
    default_sls_handler,
)


def test_default_account_setup(users):
    """Test default user account setup."""
    user = User.query.filter_by(email="federico@example.com").one()
    account_info = dict(external_id=123456, external_method="external", other="foo")

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
    attrs = dict(
        email=["federico@example.com"],
        name=["federico"],
        surname=["Fernandez"],
        external_id=["12345679abcdf"],
    )

    acs_handler = acs_handler_factory("test")

    with appctx.test_request_context(), patch(
        "flask_sso_saml.utils.SAMLAuth"
    ) as mock_saml_auth:
        mock_saml_auth.get_attributes.return_value = attrs
        next_url = acs_handler(mock_saml_auth, "/foo")

        assert next_url == "/foo"
        assert current_user.is_authenticated
        assert current_user.confirmed_at == None


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
        "flask_sso_saml.utils.SAMLAuth"
    ) as mock_saml_auth:
        mock_saml_auth.get_attributes.return_value = attrs
        next_url = acs_handler(mock_saml_auth, "/foo")

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
        "flask_sso_saml.utils.SAMLAuth"
    ) as mock_saml_auth, patch(
        "invenio_saml.handlers.account_authenticate"
    ) as mock_authenticate:
        mock_saml_auth.get_attributes.return_value = attrs
        mock_authenticate.return_value = False
        with pytest.raises(Unauthorized):
            next_url = acs_handler(mock_saml_auth, "/foo")


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
        "flask_sso_saml.utils.SAMLAuth"
    ) as mock_saml_auth, patch(
        "invenio_saml.handlers.account_register"
    ) as mock_register:
        mock_saml_auth.get_attributes.return_value = attrs
        mock_register.return_value = None
        with pytest.raises(Unauthorized):
            next_url = acs_handler(mock_saml_auth, "/foo")
