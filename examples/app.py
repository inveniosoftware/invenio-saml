# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Esteban J. Garcia Gabancho.
#
# Invenio-SAML is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Minimal Flask application example.

SPHINX-START


We will use `OneLogin <https://www.onelogin.com/>`_ to demonstrate how to
configure and use Invenio-SAML. (You should create a free developer account)

1. Register your app OneLogin (you might choose any IdP of your liking):

   - ``https://0.0.0.0:5000/saml/acs/onelogin``: SAML Consumer URL
   - ``https://0.0.0.0:5000/saml/sls/onelogin``: SAML Single Logout URL
   - ``https://0.0.0.0:5000/saml/metadata/onelogin``: SAML Audience
   - ``https://0.0.0.0:5000/saml/acs/onelogin``: SAML Recipient

2. Ensure you have ``gunicorn`` package installed:

   .. code-block:: console

      pip install gunicorn

3. Ensure you have ``openssl`` installed in your system (Most of the Linux
   distributions has it by default.).

3. Grab the *Issuer URL*, *SAML 2.0 Endpoint (HTTP)*,
   *SLO Endpoint (HTTP)* and *X.509 Certificate* after registering the
   application (they are under the SSO tab) and add them to your instance
   configuration.

   .. code-block:: console

       $ export IDP_ENTITY_ID='https://app.onelogin.com/saml/metadata/....'
       $ export IDP_SSO_URL='https://myapp-dev.onelogin.com/trust/saml2/http-post/sso/....'
       $ export IDP_SLS_URL='https://myapp-dev.onelogin.com/trust/saml2/http-redirect/slo/....'
       $ export IDP_CERT='one_line_certificate'


4. Install Flask-SSO-SAML and setup the application by running:

   .. code-block:: console

       $ pip install -e .[all]
       $ cd examples
       $ ./app-setup.sh

5. Create the key and the certificate in order to run a HTTPS server:

   .. code-block:: console

       $ openssl genrsa 1024 > instance/ssl.key
       $ openssl req -new -x509 -nodes -sha1 -key instance/ssl.key > instance/ssl.crt

6. Run gunicorn server:

   .. code-block:: console

       $ gunicorn -b :5000 --certfile=./instance/ssl.crt --keyfile=./instance/ssl.key app:app

7. Open in a browser the page `<https://0.0.0.0:5000/>`_.

8. To reset the example application run:

   .. code-block:: console

       $ ./app-teardown.sh

SPHINX-END
"""

from __future__ import absolute_import, print_function

import os

from flask import Flask, redirect, url_for
from flask_babelex import Babel
from flask_login import current_user
from flask_menu import Menu as FlaskMenu
from invenio_accounts import InvenioAccounts
from invenio_accounts.views import blueprint as blueprint_user
from invenio_db import InvenioDB
from invenio_mail import InvenioMail
from invenio_userprofiles import InvenioUserProfiles
from invenio_userprofiles.views import \
    blueprint_ui_init as blueprint_userprofile_init

from invenio_saml import InvenioSAML
from invenio_saml.handlers import acs_handler_factory, default_sls_handler


def account_info(info):
    """Extract user information from IdP response"""
    return dict(
        user=dict(
            email=info['User.email'][0],
            profile=dict(
                username=info['User.FirstName'][0],
                full_name=info['User.FirstName'][0])),
        external_id=info['User.email'][0],
        external_method='onelogin',
        active=True)


# Create Flask application
app = Flask(__name__)
app.config.update(
    SSO_SAML_IDPS={
        'onelogin': {
            'settings': {
                'idp': {
                    'entityId': os.environ.get('IDP_ENTITY_ID'),
                    'singleSignOnService': {
                        'url': os.environ.get('IDP_SSO_URL')
                    },
                    'singleLogoutService': {
                        'url': os.environ.get('IDP_SLS_URL')
                    },
                    'x509cert': os.environ.get('IDP_CERT'),
                },
            },
            'acs_handler': acs_handler_factory(account_info),
            'sls_handler': default_sls_handler,
        }
    },
    SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI',
                                           'sqlite:///instance/app.db'),
    SERVER_NAME='0.0.0.0:5000',
    SECRET_KEY='EXAMPLE_APP',
    DEBUG=True,
    SQLALCHEMY_ECHO=False,
    SECURITY_PASSWORD_SALT='security-password-salt',
    MAIL_SUPPRESS_SEND=True,
    TESTING=True,
    USERPROFILES_EXTEND_SECURITY_FORMS=True,
    SECURITY_CONFIRMABLE=False,
    SECURITY_SEND_REGISTER_EMAIL=False,
)

Babel(app)
FlaskMenu(app)
InvenioDB(app)
InvenioAccounts(app)
InvenioUserProfiles(app)
InvenioMail(app)
InvenioSAML(app)

app.register_blueprint(blueprint_user)
app.register_blueprint(blueprint_userprofile_init)


@app.route('/')
def index():
    """Homepage."""
    return 'Home page (without any restrictions)'


@app.route('/onelogin')
def github():
    """Try to print user email or redirect to login with github."""
    if not current_user.is_authenticated:
        return redirect(
            url_for('sso_saml.sso', idp='onelogin', next='/onelogin'))
    return 'hello {}'.format(current_user.email)
