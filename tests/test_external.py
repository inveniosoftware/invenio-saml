# SPDX-FileCopyrightText: 2019-2024 Esteban J. Garcia Gabancho.
# SPDX-License-Identifier: MIT

"""Test code that will get externalized at some point."""

import pytest

from invenio_saml.invenio_app import get_safe_redirect_target


@pytest.mark.parametrize(
    "next_url,expected",
    [
        ("/", "/"),
        ("/foo", "/foo"),
        ("http://not-safe.com", None),
        ("https://example.com", "https://example.com"),
    ],
)
def test_get_safe_redirect(base_app, next_url, expected):
    """Test get safe redirect target."""
    with base_app.test_request_context(query_string={"next": next_url}):
        safe_next = get_safe_redirect_target()
        assert safe_next == expected
