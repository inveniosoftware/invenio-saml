# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that provides SAML integration."""

from __future__ import absolute_import, print_function

from .ext import InvenioSAML
from .version import __version__

__all__ = ('__version__', 'InvenioSAML')
