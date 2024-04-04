# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Esteban J. G. Gabancho.
#
# invenio-saml is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio SAML errors."""


class IdentityProviderNotFound(Exception):
    """Raised when the identity provider is not found in the configuration."""
