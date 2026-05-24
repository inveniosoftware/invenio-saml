# SPDX-FileCopyrightText: 2024 Esteban J. G. Gabancho.
# SPDX-License-Identifier: MIT

"""Invenio SAML errors."""


class IdentityProviderNotFound(Exception):
    """Raised when the identity provider is not found in the configuration."""
