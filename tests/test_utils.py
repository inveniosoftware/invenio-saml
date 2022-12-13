# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Esteban J. G. Gabancho.
#
# Flask-SSO-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test utils."""

import pytest
from flask import request
from werkzeug.datastructures import MultiDict

from invenio_saml.utils import prepare_flask_request


@pytest.mark.parametrize(
    "test_request_ctx,expected",
    [
        (
            {},
            {
                "get_data": MultiDict([]),
                "http_host": "localhost",
                "https": "off",
                "post_data": MultiDict([]),
                "script_name": "/",
                "server_port": None,
            },
        ),
        (
            {"base_url": "https://tests.com:5000", "path": "/bar"},
            {
                "get_data": MultiDict([]),
                "http_host": "tests.com:5000",
                "https": "on",
                "post_data": MultiDict([]),
                "script_name": "/bar",
                "server_port": 5000,
            },
        ),
    ],
)
def test_prepare_flask_request(base_app, test_request_ctx, expected):
    """Test prepare flask request."""
    with base_app.test_request_context(**test_request_ctx):
        res = prepare_flask_request(request)
        assert res == expected
