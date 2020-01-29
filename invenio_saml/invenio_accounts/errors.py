# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Temporary file for, IMHO, Invenio-Accounts code."""


class AlreadyLinkedError(Exception):
    """Signifies that an account was already linked to another account."""

    def __init__(self, user, external_id):
        """Initialize exception."""
        self.user = user
        self.external_id = external_id
