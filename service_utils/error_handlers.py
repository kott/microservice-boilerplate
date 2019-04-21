import logging

import flask
import http.client
import werkzeug.exceptions

from service_utils import errors
from service_utils import filters


logger = logging.getLogger(__name__)


def configure_error_handlers(app):
    app.register_error_handler(Exception, json_error_handler)
    for status_code in http.client.responses:
        if status_code in werkzeug.exceptions.default_exceptions:
            app.register_error_handler(status_code, json_error_handler)


def json_error_handler(exc):
    if isinstance(exc, werkzeug.exceptions.HTTPException):
        return convert_http_error_response(exc.code, exc.description)
    return convert_http_error_response(http.client.INTERNAL_SERVER_ERROR,
                                       errors.ALL_ERRORS["INTERNAL_SERVER_ERROR"])


def convert_http_error_response(status_code, description):
    error = {
        'code': http.client.responses[status_code].upper().replace(' ', '_'),
        'description': description,
        'field': None,
    }
    errors = {'errors': [error]}
    response = flask.jsonify(errors)
    response.status_code = status_code
    filters.add_request_id_to_response(response)
    return response
