import logging

from flask import request

from service_utils import HEADER_REQUEST_ID


def newline_escaper(value):
    return value.replace('\n', '\\n').replace('\r', '\\r')


def request_id_adder(value):
    try:
        cid = request.headers.get(HEADER_REQUEST_ID, None)
    except RuntimeError:
        cid = None
    try:
        return u'cid:{} {}'.format(cid, value)
    except UnicodeDecodeError:
        value = value.decode('utf-8', errors='replace')
        return u'cid:{} {}'.format(cid, value)


class NewlineEscaperLogFormatter(logging.Formatter):
    message_editors = (
        request_id_adder,
        newline_escaper
    )

    def format(self, record):
        value = super(NewlineEscaperLogFormatter, self).format(record)
        for editor in self.message_editors:
            value = editor(value)
        return value
