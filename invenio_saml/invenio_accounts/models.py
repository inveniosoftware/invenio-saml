# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Temporary file for, IMHO, Invenio-Accounts code."""
from invenio_accounts import __version__ as ACCOUNTS_VERSION
from invenio_accounts.models import User
from invenio_db import db
from pkg_resources import DistributionNotFound, get_distribution, parse_version
from sqlalchemy_utils import Timestamp

HAS_USER_IDENTITY = True
if parse_version(ACCOUNTS_VERSION) < parse_version('1.2.0'):
    HAS_USER_IDENTITY = False

try:
    get_distribution('invenio-oauthclient')
    from invenio_oauthclient import __version__ as OAUTHCLIENT_VERSION

    if parse_version(OAUTHCLIENT_VERSION) < parse_version('1.2.0'):
        HAS_USER_IDENTITY = True
except DistributionNotFound:
    pass


if HAS_USER_IDENTITY:
    from invenio_oauthclient.models import UserIdentity

    __all__ = ()
else:

    class UserIdentity(db.Model, Timestamp):
        """Represent a UserIdentity record."""

        __tablename__ = 'accounts_useridentity'

        id = db.Column(db.String(255), primary_key=True, nullable=False)
        method = db.Column(db.String(255), primary_key=True, nullable=False)
        id_user = db.Column(
            db.Integer(), db.ForeignKey(User.id), nullable=False
        )

        user = db.relationship(User, backref='external_identifiers')

        __table_args__ = (
            db.Index(
                'useridentity_id_user_method', id_user, method, unique=True
            ),
        )

    __all__ = ('UserIdentity',)
