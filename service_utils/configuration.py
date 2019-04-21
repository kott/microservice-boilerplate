import logging.config
import os
import sys

from service_utils import error_handlers
from service_utils import filters
from service_utils import logging_helpers
from service_utils import wrappers

logger = logging.getLogger(__name__)


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEFAULT_CONFIG_HOME = os.path.join(BASE_DIR, 'configuration')
DEFAULT_PROFILE = 'docker'
DEFAULT_CONFIG_FILE = 'service.cfg'


def _exit_and_kill_master_process():
    sys.exit(4)


def get_runtime_profile():
    return os.getenv('SERVICES_PROFILE', DEFAULT_PROFILE)


def get_config_file():
    return os.getenv('SERVICE_CONFIG_FILE', DEFAULT_CONFIG_FILE)


def get_config_home():
    return os.path.abspath(os.getenv('SERVICES_CONFIG_HOME', DEFAULT_CONFIG_HOME))


def config_from_file(app, file_path):
    try:
        app.config.from_pyfile(file_path)
    except IOError as error:
        return (error.strerror, error.filename)
    except SyntaxError as error:
        return (error.msg, error.filename)


def verify_config(config, required_configurations):
    errors = []
    for key in required_configurations:
        if key not in config or config[key] == '':
            errors.append("required configuration '{}' is missing or empty".format(key))

    return errors


def configure_app(app, required_configurations=None):
    config_home = get_config_home()
    runtime_profile = get_runtime_profile()
    runtime_config_filename = get_config_file()
    config_runtime_error = config_from_file(app, os.path.join(config_home, runtime_profile, runtime_config_filename))
    if config_runtime_error:
        logger.fatal(config_runtime_error)
        _exit_and_kill_master_process()

    app.request_class = wrappers.ServiceRequest
    app.response_class = wrappers.ServiceResponse

    logging_helpers.configure_logging(app)
    logger.info("Loaded '{}' runtime profile config".format(runtime_profile))
    if config_runtime_error:
        logger.warning('Error {0}: {1}'.format(*config_runtime_error))

    required_configurations = required_configurations or []
    configuration_errors = verify_config(app.config, required_configurations)
    if configuration_errors:
        for error in configuration_errors:
            logger.fatal(error)
        _exit_and_kill_master_process()

    filters.configure_filters(app)
    error_handlers.configure_error_handlers(app)
