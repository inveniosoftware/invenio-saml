# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2024 Esteban J. Garcia Gabancho.
# Copyright (C) 2021-2022 Graz University of Technology.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Default handlers for SSO-SAML."""

from datetime import datetime, timezone

from flask import abort, current_app
from flask_login import current_user
from flask_security import logout_user
from invenio_db import db
from invenio_oauthclient.errors import AlreadyLinkedError
from invenio_oauthclient.utils import create_csrf_disabled_registrationform, fill_form

from .invenio_accounts.utils import (
    account_authenticate,
    account_get_user,
    account_link_external_id,
    account_register,
)
from .invenio_app import get_safe_redirect_target


def default_account_info(attributes, remote_app):
    """Return account info for remote user.

    This function uses the mappings configuration variable inside your IdP
    configuration.

    :param attributes: (dict) dictionary of data returned by identity provider.
    :param remote_app: (str) Identity provider key.

    :returns: (dict) A dictionary representing user to create or update.
    """
    remote_app_config = current_app.config["SSO_SAML_IDPS"][remote_app]

    mappings = remote_app_config["mappings"]

    affiliations_mapping = mappings.get("affiliations", None)
    if affiliations_mapping:
        affiliations = attributes[affiliations_mapping]
    else:
        affiliations = ""

    name = attributes[mappings["name"]][0]
    surname = attributes[mappings["surname"]][0]
    email = attributes[mappings["email"]][0]
    external_id = attributes[mappings["external_id"]][0]
    username = (
        remote_app + "-" + external_id.split("@")[0]
        if "@" in external_id
        else remote_app + "-" + external_id
    )

    return dict(
        user=dict(
            email=email,
            profile=dict(
                username=username,
                full_name=name + " " + surname,
                affiliations=affiliations,
            ),
        ),
        external_id=external_id,
        external_method=remote_app,
        active=True,
        confirmed_at=(
            datetime.now(timezone.utc)
            if remote_app_config.get("auto_confirm", False)
            else None
        ),
    )


def default_account_setup(user, account_info):
    """Default account setup which only links ``User`` and ``UserIdentity``."""
    try:
        account_link_external_id(
            user,
            dict(
                id=account_info["external_id"], method=account_info["external_method"]
            ),
        )
    except AlreadyLinkedError:
        pass


def default_sls_handler(auth, next_url):
    """Default SLS handler which simply logs out the user."""
    logout_user()
    next_url = (
        get_safe_redirect_target(_target=next_url)
        or current_app.config["SECURITY_POST_LOGOUT_VIEW"]
    )
    return next_url


def acs_handler_factory(
    remote_app,
    account_info=default_account_info,
    account_setup=default_account_setup,
    user_lookup=account_get_user,
):
    """Generate ACS handlers with an specific account info and setup functions.

    .. note::

        In 90% of the cases the ACS handler is going to be the same, only the
        way the information is extracted and processed from the IdP will be
        different.

    :param remote_app: string representing the name of the identity provider.

    :param account_info: callable to extract the account information from a
        dict like object. ``mappings`` key is required whe using it.
        This function is expected to return a dictionary similar to this:

        .. code-block:: python

            dict(
                user=dict(
                    email='federico@example.com',
                    profile=dict(username='federico',
                                 full_name='Federico Fernandez'),
                ),
                external_id='12345679abcdf',
                external_method='example',
                active=True
             )

        Where ``external_id`` is the ID provided by the IdP and
        ``external_method`` is the name of the IdP as in the configuration
        file (not mandatory but recommended).

    :param account_setup: callable to setup the user account with the
        corresponding IdP account information. Typically this means creating a
        new row under ``UserIdentity`` and maybe extending  ``g.identity``.

    :param user_lookup: callable to retrieve any user whose information matches
        what is returned by the `account_info` callable. This then returns a
        User object if a match is present and None if no match is found.

    :return: function to be used as ACS handler
    """

    def default_acs_handler(auth, next_url):
        """Default ACS handler.

        :para auth: A :class:`invenio_saml.utils.SAMLAuth` instance.
        :param next_url: String with the next URL to redirect to.

        :return: Next URL
        """
        if not current_user.is_authenticated:
            current_app.logger.debug(
                "Metadata received from IdP %s", auth.get_attributes()
            )
            _account_info = account_info(auth.get_attributes(), remote_app)
            current_app.logger.debug("Metadata extracted from IdP %s", _account_info)
            # TODO: signals?

            user = user_lookup(_account_info)

            if user is None:
                form = create_csrf_disabled_registrationform(remote_app)
                form = fill_form(form, _account_info["user"])
                user = account_register(
                    form, confirmed_at=_account_info["confirmed_at"]
                )

            # if registration fails ... TODO: signup?
            if user is None or not account_authenticate(user):
                abort(401)

            account_setup(user, _account_info)

        db.session.commit()

        next_url = (
            get_safe_redirect_target(_target=next_url)
            or current_app.config["SECURITY_POST_LOGIN_VIEW"]
        )
        return next_url

    return default_acs_handler
