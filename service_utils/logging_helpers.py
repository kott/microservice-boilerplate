import flask
import json
import logging.config
import os
import resource
import werkzeug

from service_utils.logging_config import LOGGING_CONFIG


logger = logging.getLogger(__name__)

LOGGABLE_CONTENT_TYPES = (
    'text/plain; charset=utf-8',
    'application/json',
    'application/json; charset=utf-8',
    'text/xml',
    'text/xml; charset=utf-8'
)

CONTENT_NOT_LOGGED_MSG = 'content not logged'

ENDPOINTS_NOT_LOGGED = ['/_heartbeat']

DEFAULT_LOG_FORMATTER_CLASS = 'service_utils.log_formatter.NewlineEscaperLogFormatter'


def _is_loggable_content_type(content_type):
    return content_type is not None and content_type.lower() in LOGGABLE_CONTENT_TYPES


def format_headers(headers):
    """Formats headers from a Flask :class:`~flask.Request` object.

    :param headers: The headers as a list of header name/value tuples.
    :return: A string with one header/value pair per line."""
    result = ''
    for header in headers:
        result = '{0}{1}: {2}\n'.format(result, header[0], header[1])
    return result


def format_body(request):
    content_type = request.headers.get('Content-Type', u'').split(';')[0]

    result = ''
    request_data = request.get_data(as_text=True)
    if len(request_data) > 0:
        result = '\nBody ({0} bytes):\n'.format(len(request_data))
        if 'application/json' in content_type:
            try:
                request_json = json.loads(request_data)
            except ValueError:
                logger.warning("Invalid JSON in request or response. %r", request_data)
                raise werkzeug.exceptions.BadRequest()
            result = result + json.dumps(request_json, sort_keys=True, indent=4)
        else:
            result = result + request_data

    return result


def log_request(sender, **extra):
    if _bypass_logging(flask.request.path):
        return

    body = (format_body(flask.request) if
            _is_loggable_content_type(flask.request.headers.get('Content-Type')) else CONTENT_NOT_LOGGED_MSG)

    logger.info(
        '----------\nRequest: {0} {1}\n{2}{3}\n----------\n'.format(
            flask.request.method, flask.request.url, format_headers(flask.request.headers),
            body))


def log_response(sender, response, **extra):
    if _bypass_logging(flask.request.path):
        return

    response_data = response.data.decode() if isinstance(response.data, bytes) else response.data
    body = (response_data if
            _is_loggable_content_type(response.headers.get('Content-Type')) else CONTENT_NOT_LOGGED_MSG)

    logger.info(
        '----------\nResponse: status code: {0}\n{1}\n{2}\n----------\n'.format(
            response.status_code, format_headers(response.headers), body))


def _bypass_logging(path):
    return path in flask.current_app.config.get('ENDPOINTS_NOT_LOGGED', [])


def collect_resource_usage(sender, **extra):
    """Store resource usage data that will to use as baseline in log_resource_usage()."""
    flask.g.resource_usage = resource.getrusage(resource.RUSAGE_SELF)


_RUSAGE_FIELD_NAMES = sorted([
    name for name in dir(resource.getrusage(resource.RUSAGE_SELF))
    if name.startswith('ru_')
])


def log_resource_usage(sender, response, **extra):
    """Logs the difference in resource usage since the last call to
    collect_resource_usage()."""

    if _bypass_logging(flask.request.path):
        return

    try:
        current = resource.getrusage(resource.RUSAGE_SELF)
        absolute_values = ' '.join(
            "{name}={value:f}".format(name=name, value=getattr(current, name))
            for name in _RUSAGE_FIELD_NAMES)
        diff_values = ' '.join(
            "{name}_diff={value:f}".format(name=name, value=(
                getattr(current, name) - getattr(flask.g.resource_usage, name)))
            for name in _RUSAGE_FIELD_NAMES)
        logger.debug(
            u'log_resource_usage: method={method} path={path} {absolute_values} {diff_values}'.format(
                method=flask.request.method,
                path=flask.request.path,
                absolute_values=absolute_values,
                diff_values=diff_values))
    except Exception:
        logger.exception('Failed to log resource usage, skipping')


def configure_logging(app):
    del app.logger.handlers[:]
    del logging.getLogger('werkzeug').handlers[:]

    log_formatter_class = os.getenv('LOG_FORMATTER_CLASS', DEFAULT_LOG_FORMATTER_CLASS)
    logging_configuration = LOGGING_CONFIG
    logging_configuration['formatters']['json']['()'] = log_formatter_class
    logging.config.dictConfig(logging_configuration)

    flask.request_started.connect(log_request, app)
    flask.request_finished.connect(log_response, app)
    flask.request_started.connect(collect_resource_usage, app)
    flask.request_finished.connect(log_resource_usage, app)
