# SPDX-FileCopyrightText: 2019 Esteban J. Garcia Gabancho.
# SPDX-FileCopyrightText: 2019-2021 CERN.
# SPDX-FileCopyrightText: 2021 Graz University of Technology.
# SPDX-FileCopyrightText: 2026 Paradigm Repositories.
# SPDX-License-Identifier: MIT

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
            allowed_hosts = current_app.config.get("TRUSTED_HOSTS", [])
            if redirect_uri.host in allowed_hosts:
                return target
            elif redirect_uri.path:
                return uricompose(
                    path=redirect_uri.path,
                    query=redirect_uri.query,
                    fragment=redirect_uri.fragment,
                )
    return None
