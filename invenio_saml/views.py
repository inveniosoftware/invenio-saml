# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2022-2024 Esteban J. G. Gabancho.
#
# invenio-saml is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""SAML integration functions."""

from functools import wraps

from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    make_response,
    redirect,
    request,
    session,
)

from invenio_saml.errors import IdentityProviderNotFound
from invenio_saml.proxies import current_sso_saml


def verify_idp(f):
    """Check if the Identity Provider is correctly exists."""

    @wraps(f)
    def inner(idp, *args, **kwargs):
        try:
            return f(idp=idp, auth=current_sso_saml.get_auth(idp), *args, **kwargs)
        except IdentityProviderNotFound:
            # IdP name not found inside the configuration
            return abort(404, "Identity Provider not found")

    return inner


@verify_idp
def metadata(idp, auth):
    """Expose XML configuration of the Service Provider (us)."""
    current_app.logger.debug("Handling metadata request for {}".format(idp))

    settings = auth.get_settings()
    sp_metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(sp_metadata)

    if errors:
        error_reason = auth.get_last_error_reason()
        if error_reason:
            errors.append(auth.get_last_error_reason())
            current_app.logger.error("Handling metadata request: {}".format(errors))
        return jsonify(errors), 401
    else:
        current_app.logger.debug("Metadata request response: {}".format(sp_metadata))
        resp = make_response(sp_metadata, 200)
        resp.headers["Content-Type"] = "text/xml"
        return resp


@verify_idp
def sso(idp, auth):
    """Send user to IdP login page (SAML single sign-on)."""
    current_app.logger.debug("SSO SAML for {}".format(idp))

    next_url = request.args.get("next", request.referrer) or request.host_url
    login = auth.login(return_to=next_url)

    current_app.logger.debug(
        "SSO Request XML: \n{}".format(auth.get_last_request_xml())
    )
    current_app.logger.debug('Redirecting to "{}" to initiate login'.format(login))

    if not login:
        # This should never happen, but just in case
        abort(401)

    return redirect(login)


@verify_idp
def acs(idp, auth):
    """Authorized handler callback (Assertion Consumer Service).

    It gets called by the IdP with SAML assertion when authentication has been
    performed.
    """
    try:
        # TODO https://github.com/onelogin/python3-saml/issues/39 ?
        auth.process_response()
    except Exception:  # TODO better exception handling
        return abort(400)

    errors = auth.get_errors()

    if errors:
        error_reason = auth.get_last_error_reason()
        if error_reason:
            errors.append(auth.get_last_error_reason())
            current_app.logger.error("Handling ACS request: {}".format(errors))
        return jsonify(errors), 401

    if not auth.is_authenticated():
        return abort(403)

    # Set SSO specific IdP metadata in the session, (used later in slo)
    session[current_app.config["SSO_SAML_SESSION_KEY_NAME_ID"]] = auth.get_nameid()
    session[current_app.config["SSO_SAML_SESSION_KEY_SESSION_INDEX"]] = (
        auth.get_session_index()
    )

    next_url = auth.acs_handler(request.form.get("RelayState")) or "/"

    return redirect(next_url)


@verify_idp
def slo(idp, auth):
    """Send user to IdP logout page (SAML single logout)."""
    name_id = session.get(current_app.config["SSO_SAML_SESSION_KEY_NAME_ID"])
    session_index = session.get(
        current_app.config["SSO_SAML_SESSION_KEY_SESSION_INDEX"]
    )

    next_url = request.args.get("next", request.referrer) or request.host_url

    logout = auth.logout(
        return_to=next_url, name_id=name_id, session_index=session_index
    )

    current_app.logger.debug(
        "SLO Request XML: \n{}".format(auth.get_last_request_xml())
    )
    current_app.logger.debug('Redirecting to "{}" to initiate logout'.format(logout))

    if not logout:
        # This should never happen, but just in case
        abort(401)

    return redirect(logout)


@verify_idp
def sls(idp, auth):
    """Logout handler callback (Single Logout Service).

    It Consumes LogoutResponse from IdP when logout has been performed.
    """
    # Process the SLO message received from IdP
    next_url = auth.process_slo(delete_session_cb=lambda: session.clear())

    errors = auth.get_errors()
    if errors:
        error_reason = auth.get_last_error_reason()
        if error_reason:
            errors.append(auth.get_last_error_reason())
            current_app.logger.error("Handling SLS request: {}".format(errors))
        return jsonify(errors), 401

    next_url = auth.sls_handler(next_url) or "/"

    return redirect(next_url)


def create_blueprint(state, import_name):
    """Create the SSO SAML extension blueprint."""
    bp = Blueprint(
        "sso_saml",
        import_name,
        url_prefix=state.url_prefix,
        template_folder="templates",
    )

    bp.add_url_rule(state.metadata_url, endpoint="metadata", view_func=metadata)

    bp.add_url_rule(
        state.sso_url, methods=["GET", "POST"], endpoint="sso", view_func=sso
    )

    bp.add_url_rule(
        state.acs_url, methods=["GET", "POST"], endpoint="acs", view_func=acs
    )

    bp.add_url_rule(
        state.slo_url, methods=["GET", "POST"], endpoint="slo", view_func=slo
    )

    bp.add_url_rule(state.sls_url, endpoint="sls", view_func=sls)

    return bp
