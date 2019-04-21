import logging.config
import flask
import os

from service_utils import configuration
from service_boilerplate.service import service

logger = logging.getLogger(__name__)

REQUIRED_CONFIGURATION = [
    'SOME_CONFIG_VALUE'  # TODO: Remove and add actual required config values
]


def build_server():
    flask_app = flask.Flask('service_boilerplate')  # TODO: rename service_boilerplate

    os.environ['SERVICES_CONFIG_HOME'] = os.path.join(os.path.dirname(__file__), '..', 'configuration')
    os.environ['SERVICE_CONFIG_FILE'] = 'service_boilerplate.cfg'  # TODO: rename service_boilerplate.cfg

    configuration.configure_app(flask_app, REQUIRED_CONFIGURATION)
    flask_app.register_blueprint(service)

    return flask_app
