# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2021-2022 Graz University of Technology.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Temporary file for, IMHO, Invenio-Accounts code."""

from __future__ import absolute_import, print_function

from flask import after_this_request, current_app
from flask_security import login_user
from flask_security.confirmable import requires_confirmation
from flask_security.registerable import register_user

# FIXME: modify import when integrated inside invenio_accounts
# from .models import User
from invenio_accounts.models import User
from invenio_oauthclient.models import UserIdentity
from werkzeug.local import LocalProxy

_security = LocalProxy(lambda: current_app.extensions["security"])

_datastore = LocalProxy(lambda: _security.datastore)


def _commit(response=None):
    _datastore.commit()
    return response


def _get_external_id(account_info):
    """Get external id from account info."""
    if all(k in account_info for k in ("external_id", "external_method")):
        return dict(
            id=account_info["external_id"], method=account_info["external_method"]
        )
    return None


def account_get_user(account_info=None):
    """Retrieve user object for the given request.

    Uses either the access token or extracted account information to retrieve
    the user object.

    :param account_info: The dictionary with the account info.
        (Default: ``None``)
    :returns: A :class:`invenio_accounts.models.User` instance or ``None``.
    """
    if account_info:
        external_id = _get_external_id(account_info)
        if external_id:
            user = UserIdentity.get_user(external_id["method"], external_id["id"])
            if user:
                return user

        email = account_info.get("user", {}).get("email")
        if email:
            return User.query.filter_by(email=email).one_or_none()
    return None


def account_authenticate(user):
    """Authenticate an ACS callback.

    :param user: A user instance.
    :returns: ``True`` if the user is successfully authenticated.
    """
    if not requires_confirmation(user):
        after_this_request(_commit)
        return login_user(user, remember=False)
    return False


def account_link_external_id(user, external_id=None):
    """Link a user to an external id.

    :param user: A :class:`invenio_accounts.models.User` instance.
    :param external_id: The external id associated with the user.
        (Default: ``None``)
    :raises invenio_oauthclient.errors.AlreadyLinkedError: Raised if already
        exists a link.
    """
    if UserIdentity.get_user(external_id["method"], external_id["id"]):
        # already linked. should be fine to just return
        # method and id form the composite primary key, so no other with these values can be linked
        return

    UserIdentity.create(user, external_id["method"], external_id["id"])


def account_register(form, confirmed_at=None):
    """Register user if possible.

    :param form: A form instance.
    :returns: A :class:`invenio_accounts.models.User` instance.
    """
    if form.validate():
        data = {
            **form.to_dict(),
            "confirmed_at": confirmed_at,
        }
        if not data.get("password"):
            data["password"] = ""
        user = register_user(**data)
        if not data["password"]:
            user.password = None
        _datastore.commit()
        return user
