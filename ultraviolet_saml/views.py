# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# ultraviolet-saml is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from flask import Blueprint, redirect, url_for, current_app
from flask_login import login_required
from flask_security import logout_user

blueprint = Blueprint(
    "ultraviolet_saml",
    __name__,
    template_folder="templates",
    static_folder="static",
)

"""Blueprint used for loading templates and static assets

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""


@blueprint.route("/saml/logout/")
@blueprint.route("/saml/logout/<idp>")
@login_required
def logout_saml(idp):
    logout_user()
    return redirect(url_for("sso_saml.slo", idp=idp))
