from service_utils import errors
from service_utils import validation

_REMOVE = object()


def assert_required_string(field_name, max_length, payload, payload_schema, min_length=1):
    assert_required_field(field_name, payload, payload_schema)
    assert_string(field_name, max_length, payload, payload_schema, min_length)
    if min_length > 0:
        fudge_payload(payload, field_name, '')
        assert_schema_validation_error(payload, field_name, errors.VALUE_TOO_SHORT, payload_schema)


def assert_required_field(field_name, payload, payload_schema):
    fudge_payload(payload, field_name, _REMOVE)
    assert_schema_validation_error(payload, field_name, errors.MISSING_FIELD, payload_schema)
    fudge_payload(payload, field_name, None)
    assert_schema_validation_error(payload, field_name, errors.INCORRECT_TYPE, payload_schema)


def assert_string(field_name, max_length, payload, payload_schema, min_length=0,
                  valid_chars=u'\u2603', invalid_chars=''):
    for valid_value in valid_chars:
        valid_char_length = 1 if min_length == 0 else min_length
        fudge_payload(payload, field_name, valid_value * valid_char_length)
        assert_no_schema_validation_error(payload, payload_schema)
        if min_length > 0:
            fudge_payload(payload, field_name, valid_value * (min_length - 1))
            assert_schema_validation_error(payload, field_name, errors.VALUE_TOO_SHORT, payload_schema)
        assert_string_max_length(field_name, max_length, valid_value, payload, payload_schema)
    for invalid_value in invalid_chars:
        invalid_char_length = 1 if min_length == 0 else min_length
        fudge_payload(payload, field_name, invalid_value * invalid_char_length)
        assert_schema_validation_error(payload, field_name, errors.NO_MATCH, payload_schema)
    if len(invalid_chars) > 0:
        fudge_payload(payload, field_name, valid_value[0] + invalid_value[0])
        assert_schema_validation_error(payload, field_name, errors.NO_MATCH, payload_schema)
    assert_invalid_types(field_name, [42, True, [], {}], payload, payload_schema)


def assert_optional_string(field_name, max_length, payload, payload_schema, min_length=0, allow_null=True):
    assert_string(field_name, max_length, payload, payload_schema, min_length)
    if min_length == 0:
        assert_empty_string_allowed(field_name, payload, payload_schema)
    if allow_null:
        fudge_payload(payload, field_name, None)
        assert_no_schema_validation_error(payload, payload_schema)
    fudge_payload(payload, field_name, _REMOVE)
    assert_no_schema_validation_error(payload, payload_schema)


def assert_empty_string_allowed(field_name, payload, payload_schema):
    fudge_payload(payload, field_name, '')
    assert_no_schema_validation_error(payload, payload_schema)


def assert_invalid_types(field_name, invalid_values, payload, payload_schema):
    for value in invalid_values:
        fudge_payload(
            payload, field_name, value)
        assert_schema_validation_error(
            payload, field_name, errors.INCORRECT_TYPE, payload_schema)


def assert_string_max_length(field_name, max_length, valid_char, payload, payload_schema, prefix=''):
    max_length_string = prefix + valid_char * (max_length - len(prefix))
    fudge_payload(payload, field_name, max_length_string)
    assert_no_schema_validation_error(payload, payload_schema)
    fudge_payload(payload, field_name, max_length_string + valid_char)
    assert_schema_validation_error(payload, field_name, errors.VALUE_TOO_LONG, payload_schema)


def assert_required_positive_integer(field_name, payload, payload_schema, or_zero=True, min_int=None, max_int=None):
    assert_required_field(field_name, payload, payload_schema)
    assert_positive_integer(field_name, payload, payload_schema, or_zero, min_int, max_int)


def assert_optional_positive_integer(field_name, payload, payload_schema, or_zero=True, min_int=None, max_int=None):
    fudge_payload(payload, field_name, _REMOVE)
    assert_no_schema_validation_error(payload, payload_schema)
    assert_positive_integer(field_name, payload, payload_schema, or_zero, min_int, max_int)


def assert_positive_integer(field_name, payload, payload_schema, or_zero=True, min_int=None, max_int=None):
    fudge_payload(payload, field_name, 0)
    if or_zero:
        assert_no_schema_validation_error(payload, payload_schema)
    else:
        assert_schema_validation_error(payload, field_name, errors.VALUE_OUT_OF_RANGE, payload_schema)

    fudge_payload(payload, field_name, -1)
    assert_schema_validation_error(payload, field_name, errors.VALUE_OUT_OF_RANGE, payload_schema)
    assert_integer(field_name, payload, payload_schema, min_int, max_int)


def assert_integer(field_name, payload, payload_schema, min_int=None, max_int=None):
    if min_int:
        fudge_payload(payload, field_name, min_int - 1)
        assert_schema_validation_error(payload, field_name, errors.VALUE_OUT_OF_RANGE, payload_schema)
    else:
        fudge_payload(payload, field_name, 1)
        assert_no_schema_validation_error(payload, payload_schema)

    if max_int:
        fudge_payload(payload, field_name, max_int + 1)
        assert_schema_validation_error(payload, field_name, errors.VALUE_OUT_OF_RANGE, payload_schema)

    assert_invalid_types(field_name, ['2', 1.1, True, [], {}], payload, payload_schema)


def assert_field_not_allowed(field_name, value, payload, payload_schema):
    fudge_payload(payload, field_name, value)
    assert_schema_validation_error(payload, field_name, errors.UNEXPECTED_PROPERTY, payload_schema)


def assert_optional_email_format(field_name, max_length, payload, payload_schema):
    assert_optional_field(field_name, 'a@example.com', payload, payload_schema)
    assert_email_format(field_name, max_length, payload, payload_schema)


def assert_email_format(field_name, max_length, payload, payload_schema):
    email_max_length = 'a' * (max_length - 12) + '@example.com'
    fudge_payload(payload, field_name, email_max_length)
    assert_no_schema_validation_error(payload, payload_schema)
    fudge_payload(payload, field_name, email_max_length.upper())
    assert_no_schema_validation_error(payload, payload_schema)
    email_too_long = 'a' + email_max_length
    fudge_payload(payload, field_name, email_too_long)
    assert_schema_validation_error(payload, field_name, errors.VALUE_TOO_LONG, payload_schema)
    invalid_types = [False, 42, [], {}]
    for email in invalid_types:
        fudge_payload(payload, field_name, email)
        assert_schema_validation_error(payload, field_name, errors.INCORRECT_TYPE, payload_schema)
    invalid_formats = [
        'something@example.org@foo',
        'something@@@@example.org',
        'something@@@@example.org@1',
        'something\u0000st@example.com',
        'something<>st@example.com',
        '@example.com',
        'example.com',
        'com',
        'lionel@example',
        'notanemail',
        '']
    for email in invalid_formats:
        fudge_payload(payload, field_name, email)
        assert_schema_validation_error(payload, field_name, errors.NO_MATCH, payload_schema)


def assert_optional_field(field_name, valid_value, payload, payload_schema):
    fudge_payload(payload, field_name, _REMOVE)
    assert_no_schema_validation_error(payload, payload_schema)
    fudge_payload(payload, field_name, valid_value)
    assert_no_schema_validation_error(payload, payload_schema)


def assert_required_http_url_format(field_name, payload, payload_schema, max_length=2000):
    assert_invalid_types(field_name, [42, True, [], {}], payload, payload_schema)
    assert_required_field(field_name, payload, payload_schema)
    assert_http_url_format(field_name, max_length, payload, payload_schema)


def assert_http_url_format(field_name, max_length, payload, payload_schema):
    invalid_urls = [
        'http',
        'https',
        'http:',
        'https:',
        'http:/',
        'http:/',
        'htt://www.google.com',
        'ftp://something.com',
        'www.google.com',
    ]
    valid_urls = [
        'http://example.com',
        'http://com',
        'https://example.com',
        'https://com',
    ]
    assert_string_max_length(
        field_name, max_length, 'a', payload, payload_schema, prefix='http://example.com/')
    assert_regex_values(field_name, valid_urls, invalid_urls, payload, payload_schema)


def assert_regex_values(field_name, valid_values, invalid_values, payload, payload_schema):
    for value in valid_values:
        fudge_payload(payload, field_name, value)
        assert_no_schema_validation_error(payload, payload_schema)
    for value in invalid_values:
        fudge_payload(payload, field_name, value)
        assert_schema_validation_error(payload, field_name, errors.NO_MATCH, payload_schema)


def assert_schema_validation_error(payload, field, error_code, payload_schema):
    error_list = validation.validate_against_schema(payload, payload_schema)

    failure_message = "Submitted {}, got {}, expected to find {}/{}".format(
        payload, error_list, field, error_code)

    found_error = any((error['field'] == field and error['code'] == error_code) for error in error_list)

    assert found_error, failure_message

    if field is not None:
        assert field in error_list[0]['description']


def assert_no_schema_validation_error(payload, payload_schema):
    error_list = validation.validate_against_schema(payload, payload_schema)
    failure_message = "Submitted %r, expected no error, got %s" % (payload, error_list)
    assert error_list == [], failure_message


def fudge_payload(payload, field_name, value):
    field_parts = field_name.split('.')
    field_parts = [int(part) if part.isdigit() else part for part in field_parts]
    for field_part in field_parts[:-1]:
        payload = payload[field_part]
    if value is _REMOVE:
        payload.pop(field_parts[-1], None)
    else:
        payload[field_parts[-1]] = value
