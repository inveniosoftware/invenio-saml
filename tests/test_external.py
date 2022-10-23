# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test code that will get externalized at some point."""

import pytest
from flask import request

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
