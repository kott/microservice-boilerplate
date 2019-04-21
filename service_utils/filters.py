import http.client
import logging

import flask


logger = logging.getLogger(__name__)

VALID_REQUEST_CONTENT_TYPES = ['application/json', 'application/json; charset=utf-8']


def _check_request_content_type():
    if len(flask.request.get_data()) > 0:
        if not flask.request.content_type or len(flask.request.content_type.strip()) == 0:
            logger.warning('Request received with no Content-Type header. Responding with UNSUPPORTED_MEDIA_TYPE.')
            flask.abort(http.client.UNSUPPORTED_MEDIA_TYPE, description="Request received with no Content-Type header.")

        content_type = flask.request.content_type.strip().lower()
        if content_type not in VALID_REQUEST_CONTENT_TYPES:
            logger.warning('Request has unsupported content type {0}.'.format(content_type))
            flask.abort(http.client.UNSUPPORTED_MEDIA_TYPE)


def _check_accept_header_type():
    if flask.request.accept_mimetypes.provided:
        if not flask.request.accept_mimetypes.accept_json:
            logger.warning('Request has unsupported accept type {0}.'.format(flask.request.accept_mimetypes))
            flask.abort(http.client.UNSUPPORTED_MEDIA_TYPE)


def configure_filters(app):
    app.before_request(_check_request_content_type)
    app.before_request(_check_accept_header_type)
    app.after_request(add_request_id_to_response)


def add_request_id_to_response(response):
    header_name = flask.request.request_id_header()
    if header_name and header_name not in response.headers:
            response.headers[header_name] = flask.request.headers[header_name]
    return response
