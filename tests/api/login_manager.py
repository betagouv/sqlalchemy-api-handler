from functools import wraps
import os
import uuid
from werkzeug.local import LocalProxy
from flask import current_app as app, jsonify, request, session
from flask_login import current_user, login_user
from sqlalchemy_api_handler import ApiErrors, ApiHandler
from sqlalchemy_api_handler.serialization import as_dict

from tests.api.models.user import User


def active_user_from_identifier(identifier):
    return User.query.filter_by(email=identifier).first()


def user_from_authbasic(identifier,
                        password=None):
    errors = ApiErrors()
    errors.status_code = 401

    if identifier is None:
        errors.add_error('identifier', 'Identifier is missing.')
    if password is None:
        errors.add_error('password', 'Password is missing.')
    errors.maybe_raise()

    user = active_user_from_identifier(identifier)

    if not user:
        errors.add_error('identifier', 'Wrong identifier')
        raise errors

    if len(user.password) == 32:  # MD5 pass from Denis' platform
        if not is_hashlib_equal(password, user.password):
            errors.add_error('password', 'Wrong password')
            raise errors
        change_password(user, password, check=False)
    elif not user.check_password(password):
        errors.add_error('password', 'Wrong password')
        raise errors

    return user


@as_dict.register(LocalProxy)
def _(local_proxy, column=None, includes=None):
    return as_dict.registry[ApiHandler](local_proxy, column=column, includes=includes)


@app.login_manager.user_loader
def get_user_with_id(user_id):
    session.permanent = True
    session_uuid = session.get('session_uuid')
    if existing_user_session(user_id, session_uuid):
        return User.query.get(user_id)
    return None


@app.login_manager.request_loader
def get_user_from_request(request_with_auth):
    auth = request_with_auth.authorization
    if not auth:
        return None
    user = user_from_authbasic(auth.username, auth.password)
    login_user(user, remember=True)
    stamp_session(user)
    return user


@app.login_manager.unauthorized_handler
def send_401():
    api_errors = ApiErrors()
    api_errors.add_error('auth', 'Authentification nécessaire')
    return jsonify([api_errors.errors]), 401
