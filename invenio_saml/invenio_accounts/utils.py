# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Temporary file for, IMHO, Invenio-Accounts code."""

from __future__ import absolute_import, print_function

from flask import after_this_request, current_app
from flask_security import login_user, logout_user
from flask_security.confirmable import requires_confirmation
from flask_security.registerable import register_user
# FIXME: modify import when integrated inside invenio_accounts
# from .models import User
from invenio_accounts.models import User
from invenio_db import db
from sqlalchemy.exc import IntegrityError
from werkzeug.local import LocalProxy

from .errors import AlreadyLinkedError
from .models import UserIdentity

_security = LocalProxy(lambda: current_app.extensions['security'])

_datastore = LocalProxy(lambda: _security.datastore)


def _commit(response=None):
    _datastore.commit()
    return response


def _get_external_id(account_info):
    """Get external id from account info."""
    if all(k in account_info for k in ('external_id', 'external_method')):
        return dict(
            id=account_info['external_id'],
            method=account_info['external_method'])
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
            user_identity = UserIdentity.query.filter_by(
                id=external_id['id'], method=external_id['method']).first()
            if user_identity:
                return user_identity.user
        email = account_info.get('user', {}).get('email')
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
    try:
        with db.session.begin_nested():
            db.session.add(
                UserIdentity(
                    id=external_id['id'],
                    method=external_id['method'],
                    id_user=user.id))
    except IntegrityError:
        raise AlreadyLinkedError(user, external_id)


def create_registrationform(*args, **kwargs):
    """Make a registration form."""
    class RegistrationForm(_security.confirm_register_form):
        password = None
        recaptcha = None

    return RegistrationForm(*args, **kwargs)


def _get_csrf_disabled_param():
    """Return the right param to disable CSRF depending on WTF-Form version.

    From Flask-WTF 0.14.0, `csrf_enabled` param has been deprecated in favor of
    `meta={csrf: True/False}`.
    """
    import flask_wtf
    from pkg_resources import parse_version
    supports_meta = parse_version(
        flask_wtf.__version__) >= parse_version("0.14.0")
    return dict(meta={'csrf': False}) if supports_meta else \
        dict(csrf_enabled=False)


def create_csrf_disabled_registrationform():
    """Create a registration form with CSRF disabled."""
    return create_registrationform(**_get_csrf_disabled_param())


def fill_form(form, data):
    """Prefill form with data.

    :param form: The form to fill.
    :param data: The data to insert in the form.
    :returns: A pre-filled form.
    """
    for (key, value) in data.items():
        if hasattr(form, key):
            if isinstance(value, dict):
                fill_form(getattr(form, key), value)
            else:
                getattr(form, key).data = value
    return form


def account_register(form):
    """Register user if possible.

    :param form: A form instance.
    :returns: A :class:`invenio_accounts.models.User` instance.
    """
    if form.validate():
        data = form.to_dict()
        if not data.get('password'):
            data['password'] = ''
        user = register_user(**data)
        if not data['password']:
            user.password = None
        _datastore.commit()
        return user
