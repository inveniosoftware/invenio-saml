# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-saml is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from flask import Blueprint

blueprint = Blueprint(
    "invenio_saml",
    __name__,
    template_folder="templates",
    static_folder="static",
)

"""Blueprint used for loading templates and static assets

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""
