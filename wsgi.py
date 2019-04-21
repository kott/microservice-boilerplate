"""
Define the WSGI application. For Flask, this is just an instance of the
Flask app, but must be named 'application' as per the WSGI standard.
"""
import sys

from service_boilerplate import bootstrap

sys.path.append('/content')

application = bootstrap.build_server()
