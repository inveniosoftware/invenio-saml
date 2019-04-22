# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Temporary file for, IMHO, Invenio-Accounts code."""

from invenio_accounts.models import User
from invenio_db import db
from sqlalchemy_utils import Timestamp


class UserIdentity(db.Model, Timestamp):
    """Represent a UserIdentity record."""

    __tablename__ = 'accounts_useridentity'

    id = db.Column(db.String(255), primary_key=True, nullable=False)
    method = db.Column(db.String(255), primary_key=True, nullable=False)
    id_user = db.Column(db.Integer(), db.ForeignKey(User.id), nullable=False)

    user = db.relationship(User, backref='external_identifiers')

    __table_args__ = (db.Index(
        'useridentity_id_user_method', id_user, method, unique=True), )


__all__ = ('UserIdentity', )
