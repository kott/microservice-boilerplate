"""
Here we define the custom request & response. This is mainly
used to add a custom reqID header to follow requests through
several services.
"""

import uuid

import flask
from werkzeug import datastructures

from service_utils import HEADER_REQUEST_ID


def _generate_request_id():
    return str(uuid.uuid4()).replace('-', '')


class ServiceRequest(flask.Request):
    def __init__(self, *args, **kwargs):
        header_name = self.request_id_header()
        header_name = 'HTTP_{0}'.format(header_name.upper().replace('-', '_'))
        args[0].pop(header_name, None)
        args[0][header_name] = _generate_request_id()

        super(ServiceRequest, self).__init__(*args, **kwargs)

    def request_id_header(self):
        return HEADER_REQUEST_ID


class ServiceResponse(flask.Response):
    def __init__(
        self,
        response=None, status=None, headers=None, mimetype=None,
        content_type='application/json', direct_passthrough=False,
    ):
        headers = datastructures.Headers(headers)
        super(ServiceResponse, self).__init__(
            response=response, status=status, headers=headers, mimetype=mimetype,
            content_type=content_type, direct_passthrough=direct_passthrough,
        )
