import http.client
from flask import make_response


def health_check():
    return make_response('', http.client.OK)


def heartbeat():
    return make_response('', http.client.OK)
