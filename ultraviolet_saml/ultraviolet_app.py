# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Temporary file for, IMHO, Invenio-App code.

All this code has been adapted and copied from Invenio-Oauthclient.
"""

from flask import current_app, request
from uritools import uricompose, urisplit


def get_safe_redirect_target(arg="next", _target=None):
    """Get URL to redirect to and ensure that it is local.

    :param arg: URL argument.
    :returns: The redirect target or ``None``.
    """
    for target in _target, request.args.get(arg), request.referrer:
        if target:
            redirect_uri = urisplit(target)
            allowed_hosts = current_app.config.get("APP_ALLOWED_HOSTS", [])
            if redirect_uri.host in allowed_hosts:
                return target
            elif redirect_uri.path:
                return uricompose(
                    path=redirect_uri.path,
                    query=redirect_uri.query,
                    fragment=redirect_uri.fragment,
                )
    return None
