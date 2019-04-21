import flask
import logging

from service_boilerplate import health


logger = logging.getLogger(__name__)


class ServiceBoilerplate(flask.Blueprint):  # TODO: Rename ServiceBoilerplate

    def __init__(self, *args, **kwargs):
        super(ServiceBoilerplate, self).__init__(*args, **kwargs)

        self.add_url_rule(
            '/_health',
            'health_check',
            health.health_check,
            methods=['GET']
        )
        self.add_url_rule(
            '/_heartbeat',
            'heartbeat',
            health.heartbeat,
            methods=['GET']
        )


service = ServiceBoilerplate('service_boilerplate', __name__)  # TODO: Rename ServiceBoilerplate
